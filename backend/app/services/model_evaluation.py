"""
Model Evaluation Service for CardioSense AI

This service provides genuine model performance evaluation using actual
predictions against ground-truth labels from the PTB-XL dataset.

IMPORTANT: This service does NOT use hardcoded/fake performance numbers.
All metrics are calculated from actual model predictions on real data.
"""

import numpy as np
import torch
import pandas as pd
import wfdb
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import json
import logging

from app.core.config import settings
from app.ml.predictor import predictor
from app.ml.preprocessing import preprocess_signal, validate_signal

logger = logging.getLogger(__name__)


# SCP code to superclass mapping (based on PTB-XL)
SCP_SUPERCLASS_MAP = {
    # NORM
    'NORM': 'NORM',
    'SR': 'NORM',
    
    # MI (Myocardial Infarction)
    'IMI': 'MI',
    'AMI': 'MI',
    'ALMI': 'MI',
    'ILMI': 'MI',
    'LMI': 'MI',
    'IPLMI': 'MI',
    'IPMI': 'MI',
    'PMI': 'MI',
    
    # STTC (ST/T Changes)
    'NST_': 'STTC',
    'NDT': 'STTC',
    'DIG': 'STTC',
    'LNGQT': 'STTC',
    'ISC_': 'STTC',
    'ISCAL': 'STTC',
    'ISCIN': 'STTC',
    'ISCIL': 'STTC',
    'ISCAS': 'STTC',
    'ISCLA': 'STTC',
    'ISCAN': 'STTC',
    'INJAS': 'STTC',
    'INJAL': 'STTC',
    'INJIN': 'STTC',
    'INJLA': 'STTC',
    'INJIL': 'STTC',
    'ANEUR': 'STTC',
    'EL': 'STTC',
    'STD_': 'STTC',
    
    # CD (Conduction Disturbance)
    'LAFB': 'CD',
    'IRBBB': 'CD',
    '1AVB': 'CD',
    'IVCD': 'CD',
    'CRBBB': 'CD',
    'CLBBB': 'CD',
    'LPFB': 'CD',
    'WPW': 'CD',
    'ILBBB': 'CD',
    '3AVB': 'CD',
    '2AVB': 'CD',
    'ABQRS': 'CD',
    'PVC': 'CD',
    
    # HYP (Hypertrophy)
    'LVH': 'HYP',
    'LAO/LAE': 'HYP',
    'RVH': 'HYP',
    'SEHYP': 'HYP',
    'RAO/RAE': 'HYP',
    'VCLVH': 'HYP'
}


class ModelEvaluator:
    """
    Evaluate model performance using actual predictions on labeled data.
    
    This evaluator:
    - Loads a labeled dataset (e.g., PTB-XL)
    - Runs the model to generate predictions
    - Compares predictions to ground truth
    - Calculates genuine performance metrics
    - Does NOT use hardcoded values
    """
    
    def __init__(self):
        self.model_classes = predictor.classes
        self.class_names = predictor.class_names
        self.config = predictor.config
        
        # Dataset paths
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.dataset_db_path = self.project_root / "ptbxl_database.csv"
        self.scp_statements_path = self.project_root / "scp_statements.csv"
        self.records_dir = self.project_root / "records100"
        
        # Evaluation results cache
        self._cached_results = None
        self._evaluation_timestamp = None
    
    def map_scp_to_superclass(self, scp_codes_str: str) -> Optional[str]:
        """
        Map SCP codes to superclass labels.
        
        Args:
            scp_codes_str: String representation of SCP codes (e.g., "{'NORM': 100.0}")
        
        Returns:
            Superclass label (NORM, MI, STTC, CD, HYP) or None
        """
        if not scp_codes_str or pd.isna(scp_codes_str):
            return None
        
        try:
            # Parse the string representation of dict
            scp_codes = eval(scp_codes_str.replace("'", '"'))
            
            # Get the highest confidence SCP code
            if not scp_codes:
                return None
            
            # Find the SCP code with highest confidence
            max_code = max(scp_codes.keys(), key=lambda k: scp_codes[k])
            
            # Map to superclass
            superclass = SCP_SUPERCLASS_MAP.get(max_code)
            
            return superclass
        except Exception as e:
            logger.warning(f"Failed to parse SCP codes '{scp_codes_str}': {e}")
            return None
    
    def load_dataset(
        self, 
        fold: Optional[int] = None,
        max_samples: Optional[int] = None
    ) -> Tuple[np.ndarray, List[str], pd.DataFrame]:
        """
        Load PTB-XL dataset for evaluation.
        
        Args:
            fold: Specific fold to load (None for all)
            max_samples: Maximum number of samples to load (None for all)
        
        Returns:
            Tuple of (signals, labels, metadata_df)
        """
        # Check if dataset files exist
        if not self.dataset_db_path.exists():
            raise FileNotFoundError(
                f"Dataset database not found at {self.dataset_db_path}. "
                "Please ensure PTB-XL dataset is properly configured."
            )
        
        if not self.records_dir.exists():
            raise FileNotFoundError(
                f"Records directory not found at {self.records_dir}. "
                "Please ensure PTB-XL records are available."
            )
        
        # Load database
        logger.info(f"Loading dataset from {self.dataset_db_path}")
        df = pd.read_csv(self.dataset_db_path)
        
        # Filter by fold if specified
        if fold is not None:
            df = df[df['strat_fold'] == fold]
            logger.info(f"Filtered to fold {fold}: {len(df)} samples")
        
        # Limit samples if specified
        if max_samples is not None and max_samples > 0:
            df = df.head(max_samples)
            logger.info(f"Limited to {max_samples} samples")
        
        # Map SCP codes to superclasses
        df['superclass'] = df['scp_codes'].apply(self.map_scp_to_superclass)
        
        # Filter out samples without valid superclass
        df = df[df['superclass'].notna()]
        df = df[df['superclass'].isin(self.model_classes)]
        
        logger.info(f"After filtering: {len(df)} valid samples")
        
        if len(df) == 0:
            raise ValueError("No valid samples found after filtering")
        
        # Load ECG signals
        signals = []
        labels = []
        valid_indices = []
        
        for idx, row in df.iterrows():
            try:
                # Get filename
                filename_lr = row['filename_lr']
                record_path = self.project_root / filename_lr
                
                if not record_path.exists():
                    logger.warning(f"Record not found: {record_path}")
                    continue
                
                # Load WFDB record
                record = wfdb.rdrecord(str(record_path.with_suffix('')))
                signal = record.p_signal
                
                # Transpose if needed (leads x samples)
                if signal.shape[0] == 1000 and signal.shape[1] == 12:
                    signal = signal.T
                
                # Validate signal
                is_valid, msg = validate_signal(signal, 12, 1000)
                if not is_valid:
                    logger.warning(f"Invalid signal for {filename_lr}: {msg}")
                    continue
                
                # Preprocess
                signal = preprocess_signal(signal)
                
                signals.append(signal)
                labels.append(row['superclass'])
                valid_indices.append(idx)
                
            except Exception as e:
                logger.warning(f"Failed to load {row['filename_lr']}: {e}")
                continue
        
        if len(signals) == 0:
            raise ValueError("No valid signals could be loaded")
        
        signals_array = np.array(signals)
        
        logger.info(f"Loaded {len(signals)} signals successfully")
        
        # Return only valid samples metadata
        valid_df = df.loc[valid_indices].copy()
        
        return signals_array, labels, valid_df
    
    def evaluate(
        self,
        fold: Optional[int] = 10,  # Default to test fold
        max_samples: Optional[int] = None,
        force_refresh: bool = False
    ) -> Dict:
        """
        Run model evaluation on the dataset.
        
        Args:
            fold: Dataset fold to evaluate (default: 10 for test)
            max_samples: Maximum samples to evaluate
            force_refresh: Force re-evaluation even if cached
        
        Returns:
            Dictionary containing evaluation results
        """
        # Check cache
        if not force_refresh and self._cached_results is not None:
            logger.info("Returning cached evaluation results")
            return self._cached_results
        
        logger.info("Starting model evaluation...")
        
        try:
            # Load dataset
            signals, labels, metadata_df = self.load_dataset(fold, max_samples)
            
            # Run predictions
            logger.info(f"Running predictions on {len(signals)} samples...")
            predictions = []
            probabilities = []
            
            for i, signal in enumerate(signals):
                try:
                    result = predictor.predict(signal)
                    predictions.append(result['prediction_code'])
                    probabilities.append(result['probabilities'])
                    
                    if (i + 1) % 100 == 0:
                        logger.info(f"Processed {i + 1}/{len(signals)} samples")
                except Exception as e:
                    logger.warning(f"Prediction failed for sample {i}: {e}")
                    predictions.append(None)
                    probabilities.append(None)
            
            # Filter out failed predictions
            valid_mask = [p is not None for p in predictions]
            labels = [l for l, v in zip(labels, valid_mask) if v]
            predictions = [p for p, v in zip(predictions, valid_mask) if v]
            probabilities = [p for p, v in zip(probabilities, valid_mask) if v]
            
            logger.info(f"Valid predictions: {len(predictions)}/{len(signals)}")
            
            if len(predictions) == 0:
                raise ValueError("No valid predictions generated")
            
            # Calculate metrics
            results = self._calculate_metrics(labels, predictions, probabilities, metadata_df)
            
            # Add metadata
            results['evaluation_info'] = {
                'timestamp': datetime.now().isoformat(),
                'model_version': self.config.get('model_version', '1.0'),
                'dataset_name': 'PTB-XL',
                'dataset_split': f'fold_{fold}' if fold else 'all',
                'num_samples': len(predictions),
                'num_classes': len(self.model_classes)
            }
            
            results['dataset_info'] = {
                'name': 'PTB-XL',
                'split': f'fold_{fold}' if fold else 'all',
                'samples': len(predictions),
                'classes': self.model_classes,
                'class_distribution': self._get_class_distribution(labels)
            }
            
            # Cache results
            self._cached_results = results
            self._evaluation_timestamp = datetime.now()
            
            logger.info("Evaluation completed successfully")
            
            return results
            
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'message': 'Evaluation failed. See logs for details.'
            }
    
    def _calculate_metrics(
        self,
        labels: List[str],
        predictions: List[str],
        probabilities: List[Dict],
        metadata_df: pd.DataFrame
    ) -> Dict:
        """Calculate performance metrics."""
        from sklearn.metrics import (
            accuracy_score,
            precision_score,
            recall_score,
            f1_score,
            confusion_matrix,
            classification_report
        )
        
        # Convert to numpy arrays
        y_true = np.array(labels)
        y_pred = np.array(predictions)
        
        # Overall metrics
        accuracy = accuracy_score(y_true, y_pred)
        
        # Multiclass metrics with different averaging methods
        precision_macro = precision_score(y_true, y_pred, average='macro', zero_division=0)
        precision_weighted = precision_score(y_true, y_pred, average='weighted', zero_division=0)
        
        recall_macro = recall_score(y_true, y_pred, average='macro', zero_division=0)
        recall_weighted = recall_score(y_true, y_pred, average='weighted', zero_division=0)
        
        f1_macro = f1_score(y_true, y_pred, average='macro', zero_division=0)
        f1_weighted = f1_score(y_true, y_pred, average='weighted', zero_division=0)
        
        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred, labels=self.model_classes)
        
        # Per-class metrics
        class_metrics = {}
        for cls in self.model_classes:
            if cls not in y_true and cls not in y_pred:
                # Class not present in data
                continue
            
            # Binary classification for this class
            y_true_binary = (y_true == cls).astype(int)
            y_pred_binary = (y_pred == cls).astype(int)
            
            tp = np.sum((y_true_binary == 1) & (y_pred_binary == 1))
            tn = np.sum((y_true_binary == 0) & (y_pred_binary == 0))
            fp = np.sum((y_true_binary == 0) & (y_pred_binary == 1))
            fn = np.sum((y_true_binary == 1) & (y_pred_binary == 0))
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            sensitivity = recall  # Same as recall for binary
            specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
            support = int(np.sum(y_true_binary))
            
            class_metrics[cls] = {
                'precision': float(precision),
                'recall': float(recall),
                'f1': float(f1),
                'sensitivity': float(sensitivity),
                'specificity': float(specificity),
                'support': support
            }
        
        # ROC-AUC (if probabilities available)
        roc_auc = None
        try:
            if probabilities and all(p is not None for p in probabilities):
                from sklearn.preprocessing import label_binarize
                from sklearn.metrics import roc_auc_score
                
                # Convert probabilities to array
                prob_array = np.array([[p.get(cls, 0) for cls in self.model_classes] for p in probabilities])
                
                # Binarize labels
                y_true_bin = label_binarize(y_true, classes=self.model_classes)
                
                # Calculate ROC-AUC (one-vs-rest)
                roc_auc = roc_auc_score(y_true_bin, prob_array, average='macro', multi_class='ovr')
        except Exception as e:
            logger.warning(f"ROC-AUC calculation failed: {e}")
        
        return {
            'status': 'available',
            'overall_metrics': {
                'accuracy': float(accuracy),
                'precision_macro': float(precision_macro),
                'precision_weighted': float(precision_weighted),
                'recall_macro': float(recall_macro),
                'recall_weighted': float(recall_weighted),
                'f1_macro': float(f1_macro),
                'f1_weighted': float(f1_weight),
                'averaging_method': 'macro and weighted'
            },
            'class_metrics': class_metrics,
            'confusion_matrix': cm.tolist(),
            'confusion_matrix_labels': self.model_classes,
            'roc_auc': float(roc_auc) if roc_auc is not None else None
        }
    
    def _get_class_distribution(self, labels: List[str]) -> Dict[str, int]:
        """Get class distribution from labels."""
        distribution = {}
        for cls in self.model_classes:
            distribution[cls] = labels.count(cls)
        return distribution
    
    def get_status(self) -> Dict:
        """Get evaluation status and availability."""
        status = {
            'status': 'unavailable',
            'reason': None,
            'dataset_available': False,
            'model_available': False,
            'last_evaluation': None
        }
        
        # Check model
        try:
            predictor.get_model()
            status['model_available'] = True
        except Exception as e:
            status['reason'] = f"Model not available: {str(e)}"
            return status
        
        # Check dataset
        if self.dataset_db_path.exists() and self.records_dir.exists():
            status['dataset_available'] = True
        else:
            status['reason'] = "Dataset not available. Please configure PTB-XL dataset."
            return status
        
        # Check if evaluation has been run
        if self._cached_results is not None:
            status['status'] = 'available'
            status['last_evaluation'] = self._evaluation_timestamp.isoformat()
        else:
            status['reason'] = "Evaluation not yet run. Call evaluate() to generate metrics."
        
        return status


# Global instance
model_evaluator = ModelEvaluator()

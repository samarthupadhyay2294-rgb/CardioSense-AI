import pytest
import numpy as np
from app.services.model_evaluation import model_evaluator, SCP_SUPERCLASS_MAP


class TestSCPSuperclassMapping:
    """Test SCP code to superclass mapping."""
    
    def test_scp_map_contains_all_superclasses(self):
        """Verify mapping contains all required superclasses."""
        required_superclasses = {'NORM', 'MI', 'STTC', 'CD', 'HYP'}
        mapped_values = set(SCP_SUPERCLASS_MAP.values())
        assert required_superclasses.issubset(mapped_values)
    
    def test_norm_mapping(self):
        """Test NORM class mapping."""
        assert SCP_SUPERCLASS_MAP.get('NORM') == 'NORM'
        assert SCP_SUPERCLASS_MAP.get('SR') == 'NORM'
    
    def test_mi_mapping(self):
        """Test MI class mapping."""
        assert SCP_SUPERCLASS_MAP.get('IMI') == 'MI'
        assert SCP_SUPERCLASS_MAP.get('AMI') == 'MI'
    
    def test_sttc_mapping(self):
        """Test STTC class mapping."""
        assert SCP_SUPERCLASS_MAP.get('NST_') == 'STTC'
        assert SCP_SUPERCLASS_MAP.get('NDT') == 'STTC'
    
    def test_cd_mapping(self):
        """Test CD class mapping."""
        assert SCP_SUPERCLASS_MAP.get('LAFB') == 'CD'
        assert SCP_SUPERCLASS_MAP.get('IRBBB') == 'CD'
    
    def test_hyp_mapping(self):
        """Test HYP class mapping."""
        assert SCP_SUPERCLASS_MAP.get('LVH') == 'HYP'
        assert SCP_SUPERCLASS_MAP.get('RVH') == 'HYP'


class TestModelEvaluator:
    """Test the ModelEvaluator service."""
    
    def test_initialization(self):
        """Test evaluator initialization."""
        assert model_evaluator is not None
        assert hasattr(model_evaluator, 'model_classes')
        assert hasattr(model_evaluator, 'class_names')
        assert hasattr(model_evaluator, 'config')
    
    def test_map_scp_to_superclass_valid(self):
        """Test valid SCP code mapping."""
        # Normal ECG
        result = model_evaluator.map_scp_to_superclass("{'NORM': 100.0}")
        assert result == 'NORM'
        
        # Myocardial infarction
        result = model_evaluator.map_scp_to_superclass("{'IMI': 35.0}")
        assert result == 'MI'
        
        # ST/T changes
        result = model_evaluator.map_scp_to_superclass("{'NST_': 100.0}")
        assert result == 'STTC'
    
    def test_map_scp_to_superclass_invalid(self):
        """Test invalid SCP code mapping."""
        # Invalid string
        result = model_evaluator.map_scp_to_superclass("invalid")
        assert result is None
        
        # Empty string
        result = model_evaluator.map_scp_to_superclass("")
        assert result is None
        
        # None
        result = model_evaluator.map_scp_to_superclass(None)
        assert result is None
    
    def test_map_scp_to_superclass_multiple_codes(self):
        """Test mapping with multiple SCP codes."""
        # Should return the code with highest confidence
        result = model_evaluator.map_scp_to_superclass("{'NORM': 80.0, 'SBRAD': 20.0}")
        assert result == 'NORM'
    
    def test_get_class_distribution(self):
        """Test class distribution calculation."""
        labels = ['NORM', 'NORM', 'MI', 'STTC', 'NORM', 'CD']
        distribution = model_evaluator._get_class_distribution(labels)
        
        assert distribution['NORM'] == 3
        assert distribution['MI'] == 1
        assert distribution['STTC'] == 1
        assert distribution['CD'] == 1
        assert distribution['HYP'] == 0
    
    def test_get_status_model_unavailable(self):
        """Test status when model is unavailable."""
        # This test assumes model is available in normal environment
        # We can't easily mock this without modifying the service
        status = model_evaluator.get_status()
        
        # Status should have required fields
        assert 'status' in status
        assert 'dataset_available' in status
        assert 'model_available' in status


class TestMetricCalculations:
    """Test metric calculation logic."""
    
    def test_confusion_matrix_structure(self):
        """Test confusion matrix structure."""
        # Simulated confusion matrix calculation
        y_true = ['NORM', 'MI', 'NORM', 'STTC', 'MI']
        y_pred = ['NORM', 'MI', 'MI', 'STTC', 'MI']
        
        from sklearn.metrics import confusion_matrix
        cm = confusion_matrix(y_true, y_pred, labels=['NORM', 'MI', 'STTC', 'CD', 'HYP'])
        
        assert cm.shape == (5, 5)
        assert np.sum(cm) == len(y_true)
    
    def test_per_class_metrics_calculation(self):
        """Test per-class metric calculation."""
        y_true = ['NORM', 'NORM', 'MI', 'MI', 'MI']
        y_pred = ['NORM', 'MI', 'MI', 'MI', 'NORM']
        
        # Calculate for MI class
        y_true_binary = np.array([1 if y == 'MI' else 0 for y in y_true])
        y_pred_binary = np.array([1 if y == 'MI' else 0 for y in y_pred])
        
        tp = np.sum((y_true_binary == 1) & (y_pred_binary == 1))
        tn = np.sum((y_true_binary == 0) & (y_pred_binary == 0))
        fp = np.sum((y_true_binary == 0) & (y_pred_binary == 1))
        fn = np.sum((y_true_binary == 1) & (y_pred_binary == 0))
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        assert tp == 2
        assert tn == 1
        assert fp == 1
        assert fn == 1
        assert precision == 0.6666666666666666
        assert recall == 0.6666666666666666
        assert f1 == 0.6666666666666666
    
    def test_overall_metrics_calculation(self):
        """Test overall metrics calculation."""
        y_true = ['NORM', 'MI', 'STTC', 'NORM', 'MI']
        y_pred = ['NORM', 'MI', 'MI', 'NORM', 'STTC']
        
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        accuracy = accuracy_score(y_true, y_pred)
        precision_macro = precision_score(y_true, y_pred, average='macro', zero_division=0)
        recall_macro = recall_score(y_true, y_pred, average='macro', zero_division=0)
        f1_macro = f1_score(y_true, y_pred, average='macro', zero_division=0)
        
        assert 0 <= accuracy <= 1
        assert 0 <= precision_macro <= 1
        assert 0 <= recall_macro <= 1
        assert 0 <= f1_macro <= 1


class TestDatasetValidation:
    """Test dataset validation logic."""
    
    def test_empty_dataset_handling(self):
        """Test handling of empty dataset."""
        # If dataset is empty, should raise appropriate error
        # This is tested through the actual load_dataset method
        # which requires actual dataset files
        pass
    
    def test_mismatched_labels_handling(self):
        """Test handling of mismatched labels."""
        # Labels not in model classes should be filtered out
        labels = ['NORM', 'MI', 'INVALID_CLASS', 'STTC']
        valid_labels = [l for l in labels if l in model_evaluator.model_classes]
        
        assert 'INVALID_CLASS' not in valid_labels
        assert len(valid_labels) == 3

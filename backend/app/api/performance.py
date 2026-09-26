"""
Performance API Endpoints

Provides endpoints for model performance metrics and evaluation results.
All metrics are calculated from actual model predictions, not hardcoded.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging

from app.services.model_evaluation import model_evaluator

logger = logging.getLogger(__name__)

router = APIRouter(tags=["performance"])


@router.get("/api/performance/status")
async def get_performance_status():
    """
    Get the status of model evaluation availability.
    
    Returns information about whether:
    - Model is available
    - Dataset is available
    - Evaluation has been run
    - Last evaluation timestamp
    """
    try:
        status = model_evaluator.get_status()
        return status
    except Exception as e:
        logger.error(f"Failed to get performance status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.get("/api/performance/metrics")
async def get_performance_metrics(
    fold: Optional[int] = Query(10, description="Dataset fold to evaluate"),
    max_samples: Optional[int] = Query(None, description="Maximum samples to evaluate"),
    force: bool = Query(False, description="Force re-evaluation")
):
    """
    Get model performance metrics.
    
    Returns calculated metrics including:
    - Overall metrics (accuracy, precision, recall, F1)
    - Per-class metrics
    - Confusion matrix
    - ROC-AUC (if available)
    - Dataset information
    - Evaluation metadata
    
    If evaluation has not been run, it will be triggered automatically.
    """
    try:
        # Check status first
        status = model_evaluator.get_status()
        
        if status['status'] == 'unavailable':
            return {
                'status': 'unavailable',
                'reason': status['reason'],
                'dataset_available': status['dataset_available'],
                'model_available': status['model_available']
            }
        
        # Run or get evaluation
        results = model_evaluator.evaluate(
            fold=fold,
            max_samples=max_samples,
            force_refresh=force
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@router.get("/api/performance/confusion-matrix")
async def get_confusion_matrix(
    fold: Optional[int] = Query(10, description="Dataset fold to evaluate"),
    normalize: bool = Query(False, description="Return normalized percentages")
):
    """
    Get the confusion matrix.
    
    Args:
        fold: Dataset fold to evaluate
        normalize: If True, return normalized percentages instead of raw counts
    
    Returns:
        Confusion matrix with labels
    """
    try:
        status = model_evaluator.get_status()
        
        if status['status'] == 'unavailable':
            raise HTTPException(
                status_code=503,
                detail=f"Evaluation not available: {status['reason']}"
            )
        
        results = model_evaluator.evaluate(fold=fold)
        
        if results['status'] == 'error':
            raise HTTPException(status_code=500, detail=results.get('error'))
        
        cm = results['confusion_matrix']
        labels = results['confusion_matrix_labels']
        
        if normalize:
            # Normalize by row (actual class)
            cm_normalized = []
            for row in cm:
                row_sum = sum(row)
                if row_sum > 0:
                    cm_normalized.append([x / row_sum for x in row])
                else:
                    cm_normalized.append([0.0] * len(row))
            cm = cm_normalized
        
        return {
            'confusion_matrix': cm,
            'labels': labels,
            'normalized': normalize
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get confusion matrix: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get confusion matrix: {str(e)}")


@router.get("/api/performance/classes")
async def get_class_metrics(
    fold: Optional[int] = Query(10, description="Dataset fold to evaluate")
):
    """
    Get per-class performance metrics.
    
    Returns detailed metrics for each class including:
    - Precision
    - Recall
    - F1-score
    - Sensitivity
    - Specificity
    - Support (sample count)
    """
    try:
        status = model_evaluator.get_status()
        
        if status['status'] == 'unavailable':
            raise HTTPException(
                status_code=503,
                detail=f"Evaluation not available: {status['reason']}"
            )
        
        results = model_evaluator.evaluate(fold=fold)
        
        if results['status'] == 'error':
            raise HTTPException(status_code=500, detail=results.get('error'))
        
        return {
            'class_metrics': results['class_metrics'],
            'class_labels': results['confusion_matrix_labels']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get class metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get class metrics: {str(e)}")


@router.post("/api/performance/evaluate")
async def trigger_evaluation(
    fold: Optional[int] = Query(10, description="Dataset fold to evaluate"),
    max_samples: Optional[int] = Query(None, description="Maximum samples to evaluate")
):
    """
    Trigger a new model evaluation.
    
    This endpoint forces a re-evaluation even if cached results exist.
    Use this to update metrics after model changes or dataset updates.
    """
    try:
        status = model_evaluator.get_status()
        
        if not status['model_available']:
            raise HTTPException(
                status_code=503,
                detail="Model not available"
            )
        
        if not status['dataset_available']:
            raise HTTPException(
                status_code=503,
                detail="Dataset not available"
            )
        
        results = model_evaluator.evaluate(
            fold=fold,
            max_samples=max_samples,
            force_refresh=True
        )
        
        if results['status'] == 'error':
            raise HTTPException(status_code=500, detail=results.get('error'))
        
        return {
            'status': 'success',
            'message': 'Evaluation completed',
            'results': results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to trigger evaluation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to trigger evaluation: {str(e)}")

"""
Model Evaluation Script

This script provides a reproducible entry point for model evaluation.
It loads the model, dataset, runs predictions, and calculates metrics.

Usage:
    python scripts/evaluate_model.py --fold 10 --max-samples 1000
    python scripts/evaluate_model.py --output results.json
"""

import argparse
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.model_evaluation import model_evaluator
from app.core.config import settings


def main():
    parser = argparse.ArgumentParser(description="Evaluate CardioSense AI model performance")
    parser.add_argument(
        "--fold",
        type=int,
        default=10,
        help="Dataset fold to evaluate (default: 10 for test set)"
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="Maximum number of samples to evaluate (default: all)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output JSON file for results (default: print to stdout)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-evaluation even if cached results exist"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("CardioSense AI Model Evaluation")
    print("=" * 60)
    print(f"Model path: {settings.MODEL_PATH}")
    print(f"Config path: {settings.MODEL_CONFIG_PATH}")
    print(f"Dataset fold: {args.fold}")
    print(f"Max samples: {args.max_samples if args.max_samples else 'All'}")
    print("=" * 60)
    
    # Check status first
    status = model_evaluator.get_status()
    print(f"\nStatus Check:")
    print(f"  Model available: {status['model_available']}")
    print(f"  Dataset available: {status['dataset_available']}")
    
    if status['status'] == 'unavailable':
        print(f"\nERROR: {status['reason']}")
        return 1
    
    # Run evaluation
    print(f"\nRunning evaluation...")
    try:
        results = model_evaluator.evaluate(
            fold=args.fold,
            max_samples=args.max_samples,
            force_refresh=args.force
        )
    except Exception as e:
        print(f"\nERROR: Evaluation failed: {e}")
        return 1
    
    # Display results
    if results['status'] == 'error':
        print(f"\nERROR: {results.get('error', 'Unknown error')}")
        return 1
    
    print(f"\n{'=' * 60}")
    print("Evaluation Results")
    print(f"{'=' * 60}")
    
    # Overall metrics
    overall = results['overall_metrics']
    print(f"\nOverall Metrics:")
    print(f"  Accuracy: {overall['accuracy']:.4f}")
    print(f"  Precision (macro): {overall['precision_macro']:.4f}")
    print(f"  Precision (weighted): {overall['precision_weighted']:.4f}")
    print(f"  Recall (macro): {overall['recall_macro']:.4f}")
    print(f"  Recall (weighted): {overall['recall_weighted']:.4f}")
    print(f"  F1 (macro): {overall['f1_macro']:.4f}")
    print(f"  F1 (weighted): {overall['f1_weighted']:.4f}")
    
    if results.get('roc_auc') is not None:
        print(f"  ROC-AUC: {results['roc_auc']:.4f}")
    
    # Class metrics
    print(f"\nPer-Class Metrics:")
    for cls, metrics in results['class_metrics'].items():
        print(f"\n  {cls}:")
        print(f"    Precision: {metrics['precision']:.4f}")
        print(f"    Recall: {metrics['recall']:.4f}")
        print(f"    F1: {metrics['f1']:.4f}")
        print(f"    Sensitivity: {metrics['sensitivity']:.4f}")
        print(f"    Specificity: {metrics['specificity']:.4f}")
        print(f"    Support: {metrics['support']}")
    
    # Dataset info
    dataset = results['dataset_info']
    print(f"\nDataset Information:")
    print(f"  Name: {dataset['name']}")
    print(f"  Split: {dataset['split']}")
    print(f"  Samples: {dataset['samples']}")
    print(f"  Classes: {', '.join(dataset['classes'])}")
    print(f"\n  Class Distribution:")
    for cls, count in dataset['class_distribution'].items():
        pct = count / dataset['samples'] * 100
        print(f"    {cls}: {count} ({pct:.1f}%)")
    
    # Evaluation info
    eval_info = results['evaluation_info']
    print(f"\nEvaluation Information:")
    print(f"  Timestamp: {eval_info['timestamp']}")
    print(f"  Model version: {eval_info['model_version']}")
    
    # Save to file if specified
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to: {output_path}")
    
    print(f"\n{'=' * 60}")
    print("Evaluation completed successfully")
    print(f"{'=' * 60}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

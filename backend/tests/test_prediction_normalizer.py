"""
Tests for Prediction Normalizer
"""

import pytest
from app.ml.prediction_normalizer import prediction_normalizer


class TestPredictionNormalizer:
    """Test suite for prediction normalization."""
    
    def test_normalize_signal_prediction_basic(self):
        """Test basic signal prediction normalization."""
        prediction_result = {
            "prediction": "Normal",
            "prediction_code": "NORM",
            "confidence": 0.85,
            "probabilities": {
                "Normal": 0.85,
                "Myocardial Infarction": 0.10,
                "ST/T Changes": 0.05
            },
            "all_predictions": {
                "Normal": True,
                "Myocardial Infarction": False,
                "ST/T Changes": False
            },
            "model_version": "1.0",
            "processing_time": 0.123
        }
        
        result = prediction_normalizer.normalize_signal_prediction(prediction_result)
        
        assert result["input_type"] == "ecg_signal"
        assert result["model"] == "1.0"
        assert result["primary_prediction"] == "Normal"
        assert result["prediction_code"] == "NORM"
        assert result["confidence"] == 0.85
        assert result["probabilities"]["Normal"] == 0.85
        assert result["all_predictions"]["Normal"] is True
        assert result["model_metadata"]["model_version"] == "1.0"
        assert result["model_metadata"]["processing_time"] == 0.123
    
    def test_normalize_signal_prediction_with_features(self):
        """Test signal prediction normalization with detailed features."""
        prediction_result = {
            "prediction": "Myocardial Infarction",
            "prediction_code": "MI",
            "confidence": 0.92,
            "probabilities": {"Myocardial Infarction": 0.92},
            "all_predictions": {"Myocardial Infarction": True},
            "model_version": "1.0",
            "processing_time": 0.15
        }
        
        detailed_features = {
            "temporal": {"I": {"heart_rate": {"mean": 75}}},
            "frequency": {"dominant_freq": 1.2}
        }
        
        signal_quality = "good"
        
        clinical_interpretation = {
            "primary_findings": ["Signs of myocardial infarction"],
            "urgency": "emergency"
        }
        
        result = prediction_normalizer.normalize_signal_prediction(
            prediction_result,
            detailed_features=detailed_features,
            signal_quality=signal_quality,
            clinical_interpretation=clinical_interpretation
        )
        
        assert result["existing_interpretation"]["detailed_features"] == detailed_features
        assert result["existing_interpretation"]["signal_quality"] == signal_quality
        assert result["existing_interpretation"]["clinical_interpretation"] == clinical_interpretation
    
    def test_normalize_image_prediction_basic(self):
        """Test basic image prediction normalization."""
        prediction_result = {
            "prediction": "N",
            "prediction_code": "N",
            "confidence": 0.78,
            "probabilities": {
                "N": 0.78,
                "L": 0.10,
                "R": 0.08
            },
            "model_name": "EfficientNet-B0",
            "model_version": "1.0",
            "processing_time": 0.089
        }
        
        result = prediction_normalizer.normalize_image_prediction(prediction_result)
        
        assert result["input_type"] == "ecg_image"
        assert result["model"] == "EfficientNet-B0"
        assert result["primary_prediction"] == "N"
        assert result["prediction_code"] == "N"
        assert result["confidence"] == 0.78
        assert result["probabilities"]["N"] == 0.78
        assert result["model_metadata"]["model_name"] == "EfficientNet-B0"
        assert result["model_metadata"]["model_version"] == "1.0"
    
    def test_normalize_image_prediction_with_interpretation(self):
        """Test image prediction normalization with interpretation."""
        prediction_result = {
            "prediction": "V",
            "prediction_code": "V",
            "confidence": 0.65,
            "probabilities": {"V": 0.65},
            "model_name": "EfficientNet-B0",
            "model_version": "1.0",
            "processing_time": 0.095
        }
        
        interpretation = {
            "dominant_group": "Ventricular",
            "group_probabilities": {
                "Normal": 0.20,
                "Ventricular": 0.65,
                "Supraventricular": 0.15
            },
            "subclass_results": [
                {
                    "raw_class": "V",
                    "human_readable_label": "Ventricular Premature Beat (PVC)",
                    "probability": 0.65,
                    "group": "Ventricular"
                }
            ],
            "pattern_summary": "The model predicts a ventricular pattern.",
            "recommended_next_steps": ["Professional review recommended"]
        }
        
        result = prediction_normalizer.normalize_image_prediction(
            prediction_result,
            interpretation=interpretation
        )
        
        assert result["group"] == "Ventricular"
        assert result["group_probabilities"]["Ventricular"] == 0.65
        assert len(result["subclass_results"]) == 1
        assert result["pattern_summary"] == "The model predicts a ventricular pattern."
        assert len(result["recommended_next_steps"]) == 1
    
    def test_normalize_from_analysis_dict_signal(self):
        """Test normalization from signal analysis dictionary."""
        analysis = {
            "id": 1,
            "analysis_type": "signal",
            "prediction": "ST/T Changes",
            "prediction_code": "STTC",
            "confidence": 0.73,
            "probabilities": {"ST/T Changes": 0.73},
            "all_predictions": {"ST/T Changes": True},
            "model_version": "1.0",
            "processing_time": 0.14,
            "signal_quality": "fair",
            "detailed_features": {"temporal": {}},
            "clinical_interpretation": {"primary_findings": ["ST/T changes"]}
        }
        
        result = prediction_normalizer.normalize_from_analysis_dict(analysis)
        
        assert result["input_type"] == "ecg_signal"
        assert result["primary_prediction"] == "ST/T Changes"
        assert result["existing_interpretation"]["signal_quality"] == "fair"
        assert result["existing_interpretation"]["detailed_features"] == {"temporal": {}}
    
    def test_normalize_from_analysis_dict_image(self):
        """Test normalization from image analysis dictionary."""
        analysis = {
            "id": 2,
            "analysis_type": "image",
            "prediction": "Normal Beat",
            "prediction_code": "N",
            "confidence": 0.88,
            "probabilities": {"N": 0.88},
            "model_name": "EfficientNet-B0",
            "model_version": "1.0",
            "processing_time": 0.076,
            "dominant_group": "Normal",
            "group_probabilities": {"Normal": 0.88},
            "subclass_results": [],
            "pattern_summary": "Normal pattern detected.",
            "recommended_next_steps": ["Routine follow-up"]
        }
        
        result = prediction_normalizer.normalize_from_analysis_dict(analysis)
        
        assert result["input_type"] == "ecg_image"
        assert result["primary_prediction"] == "Normal Beat"
        assert result["group"] == "Normal"
        assert result["pattern_summary"] == "Normal pattern detected."
    
    def test_probabilities_preserved_signal(self):
        """Test that probabilities are preserved in signal normalization."""
        original_probs = {
            "Normal": 0.70,
            "Myocardial Infarction": 0.20,
            "ST/T Changes": 0.07,
            "Conduction Disturbance": 0.02,
            "Hypertrophy": 0.01
        }
        
        prediction_result = {
            "prediction": "Normal",
            "prediction_code": "NORM",
            "confidence": 0.70,
            "probabilities": original_probs.copy(),
            "all_predictions": {"Normal": True},
            "model_version": "1.0",
            "processing_time": 0.1
        }
        
        result = prediction_normalizer.normalize_signal_prediction(prediction_result)
        
        # Verify probabilities are preserved exactly
        for key, value in original_probs.items():
            assert result["probabilities"][key] == value
    
    def test_probabilities_preserved_image(self):
        """Test that probabilities are preserved in image normalization."""
        original_probs = {
            "N": 0.60,
            "L": 0.15,
            "R": 0.10,
            "A": 0.08,
            "V": 0.07
        }
        
        prediction_result = {
            "prediction": "N",
            "prediction_code": "N",
            "confidence": 0.60,
            "probabilities": original_probs.copy(),
            "model_name": "EfficientNet-B0",
            "model_version": "1.0",
            "processing_time": 0.08
        }
        
        result = prediction_normalizer.normalize_image_prediction(prediction_result)
        
        # Verify probabilities are preserved exactly
        for key, value in original_probs.items():
            assert result["probabilities"][key] == value
    
    def test_confidence_preserved(self):
        """Test that confidence values are preserved."""
        prediction_result = {
            "prediction": "Myocardial Infarction",
            "prediction_code": "MI",
            "confidence": 0.9543,
            "probabilities": {"Myocardial Infarction": 0.9543},
            "all_predictions": {"Myocardial Infarction": True},
            "model_version": "1.0",
            "processing_time": 0.12
        }
        
        result = prediction_normalizer.normalize_signal_prediction(prediction_result)
        
        assert result["confidence"] == 0.9543
    
    def test_missing_optional_fields(self):
        """Test normalization with missing optional fields."""
        prediction_result = {
            "prediction": "Normal",
            "prediction_code": "NORM",
            "confidence": 0.80,
            "probabilities": {"Normal": 0.80},
            "all_predictions": {"Normal": True},
            "model_version": "1.0",
            "processing_time": 0.1
        }
        
        # Should not raise error with missing optional fields
        result = prediction_normalizer.normalize_signal_prediction(prediction_result)
        
        assert result["existing_interpretation"]["clinical_interpretation"] is None
        assert result["existing_interpretation"]["detailed_features"] is None
        assert result["existing_interpretation"]["signal_quality"] is None

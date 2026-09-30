"""
Tests for Clinical Context Builder
"""

import pytest
from app.services.clinical_context import clinical_context_builder


class TestClinicalContextBuilder:
    """Test suite for clinical context builder."""
    
    def test_build_signal_context(self):
        """Test building context for signal predictions."""
        normalized_prediction = {
            "input_type": "ecg_signal",
            "model": "ECGCNN",
            "primary_prediction": "Myocardial Infarction",
            "prediction_code": "MI",
            "confidence": 0.86,
            "probabilities": {
                "NORM": 0.04,
                "MI": 0.86,
                "STTC": 0.32,
                "CD": 0.05,
                "HYP": 0.11
            },
            "all_predictions": {"MI": True},
            "existing_interpretation": {}
        }
        
        context = clinical_context_builder.build_context(normalized_prediction)
        
        assert context["input_type"] == "ecg_signal"
        assert context["prediction_code"] == "MI"
        assert context["confidence"] == 0.86
        assert context["confidence_level"] == "high"
        assert "ecg_finding" in context
        assert "possible_associations" in context
        assert "limitations" in context
        assert "safety_instructions" in context
        assert context["non_diagnostic_requirement"] is True
    
    def test_build_image_context(self):
        """Test building context for image predictions."""
        normalized_prediction = {
            "input_type": "ecg_image",
            "model": "EfficientNet-B0",
            "primary_prediction": "PVC",
            "prediction_code": "V",
            "confidence": 0.91,
            "group": "Ventricular",
            "group_probabilities": {"Ventricular": 0.91},
            "existing_interpretation": {}
        }
        
        context = clinical_context_builder.build_context(normalized_prediction)
        
        assert context["input_type"] == "ecg_image"
        assert context["prediction_code"] == "V"
        assert context["confidence"] == 0.91
        assert context["confidence_level"] == "high"
        assert context["group"] == "Ventricular"
        assert "ecg_finding" in context
        assert "possible_associations" in context
    
    def test_confidence_assessment_high(self):
        """Test confidence assessment for high confidence."""
        assert clinical_context_builder._assess_confidence_level(0.85) == "high"
        assert clinical_context_builder._assess_confidence_level(0.90) == "high"
    
    def test_confidence_assessment_moderate(self):
        """Test confidence assessment for moderate confidence."""
        assert clinical_context_builder._assess_confidence_level(0.70) == "moderate"
        assert clinical_context_builder._assess_confidence_level(0.65) == "moderate"
    
    def test_confidence_assessment_low(self):
        """Test confidence assessment for low confidence."""
        assert clinical_context_builder._assess_confidence_level(0.50) == "low"
        assert clinical_context_builder._assess_confidence_level(0.45) == "low"
    
    def test_confidence_assessment_very_low(self):
        """Test confidence assessment for very low confidence."""
        assert clinical_context_builder._assess_confidence_level(0.30) == "very_low"
        assert clinical_context_builder._assess_confidence_level(0.15) == "very_low"
    
    def test_signal_mi_associations(self):
        """Test MI signal associations are conservative."""
        normalized_prediction = {
            "input_type": "ecg_signal",
            "model": "ECGCNN",
            "primary_prediction": "Myocardial Infarction",
            "prediction_code": "MI",
            "confidence": 0.86,
            "probabilities": {"MI": 0.86},
            "all_predictions": {"MI": True},
            "existing_interpretation": {}
        }
        
        context = clinical_context_builder.build_context(normalized_prediction)
        
        # Check that associations use conservative language
        associations = context["possible_associations"]
        assert len(associations) > 0
        # Should not contain definitive language
        for assoc in associations:
            assert "definitely" not in assoc.lower()
            assert "confirms" not in assoc.lower()
    
    def test_signal_normal_associations(self):
        """Test Normal signal associations."""
        normalized_prediction = {
            "input_type": "ecg_signal",
            "model": "ECGCNN",
            "primary_prediction": "Normal",
            "prediction_code": "NORM",
            "confidence": 0.95,
            "probabilities": {"Normal": 0.95},
            "all_predictions": {"Normal": True},
            "existing_interpretation": {}
        }
        
        context = clinical_context_builder.build_context(normalized_prediction)
        
        assert context["prediction_code"] == "NORM"
        assert "Normal sinus rhythm" in context["ecg_finding"]
    
    def test_unsupported_input_type(self):
        """Test that unsupported input type raises error."""
        normalized_prediction = {
            "input_type": "unsupported_type",
            "model": "Unknown",
            "primary_prediction": "Unknown",
            "confidence": 0.5
        }
        
        with pytest.raises(ValueError) as exc_info:
            clinical_context_builder.build_context(normalized_prediction)
        
        assert "Unsupported input_type" in str(exc_info.value)
    
    def test_safety_instructions_present(self):
        """Test that safety instructions are included."""
        normalized_prediction = {
            "input_type": "ecg_signal",
            "model": "ECGCNN",
            "primary_prediction": "Normal",
            "prediction_code": "NORM",
            "confidence": 0.85,
            "probabilities": {"Normal": 0.85},
            "all_predictions": {"Normal": True},
            "existing_interpretation": {}
        }
        
        context = clinical_context_builder.build_context(normalized_prediction)
        
        safety_instructions = context["safety_instructions"]
        assert len(safety_instructions) > 0
        assert any("NOT diagnosing" in instr for instr in safety_instructions)

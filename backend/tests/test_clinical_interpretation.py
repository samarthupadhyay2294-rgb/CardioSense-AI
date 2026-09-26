import pytest
import numpy as np
from app.services.clinical_interpretation import clinical_interpreter


class TestClinicalInterpreter:
    """Test the clinical interpretation service."""
    
    def test_initialization(self):
        """Test interpreter initialization."""
        assert clinical_interpreter is not None
        assert hasattr(clinical_interpreter, 'clinical_rules')
        assert hasattr(clinical_interpreter, 'thresholds')
    
    def test_interpret_normal(self):
        """Test interpretation of normal prediction."""
        prediction = {
            "prediction": "Normal",
            "prediction_code": "NORM",
            "confidence": 0.95
        }
        
        interpretation = clinical_interpreter.interpret_prediction(prediction)
        
        assert interpretation["urgency"] == "none"
        assert len(interpretation["primary_findings"]) > 0
        assert "Normal" in interpretation["primary_findings"][0] or "normal" in interpretation["primary_findings"][0].lower()
        assert len(interpretation["recommendations"]) > 0
        assert len(interpretation["limitations"]) > 0
    
    def test_interpret_mi(self):
        """Test interpretation of MI prediction."""
        prediction = {
            "prediction": "Myocardial Infarction",
            "prediction_code": "MI",
            "confidence": 0.85
        }
        
        interpretation = clinical_interpreter.interpret_prediction(prediction)
        
        assert interpretation["urgency"] == "emergency"
        assert len(interpretation["primary_findings"]) > 0
        assert len(interpretation["recommendations"]) > 0
        assert len(interpretation["differential_diagnosis"]) > 0
        assert "emergency" in interpretation["clinical_significance"].lower()
    
    def test_interpret_sttc(self):
        """Test interpretation of STTC prediction."""
        prediction = {
            "prediction": "ST/T Changes",
            "prediction_code": "STTC",
            "confidence": 0.75
        }
        
        interpretation = clinical_interpreter.interpret_prediction(prediction)
        
        assert interpretation["urgency"] == "urgent"
        assert len(interpretation["primary_findings"]) > 0
        assert len(interpretation["recommendations"]) > 0
        assert len(interpretation["differential_diagnosis"]) > 0
    
    def test_interpret_cd(self):
        """Test interpretation of CD prediction."""
        prediction = {
            "prediction": "Conduction Disturbance",
            "prediction_code": "CD",
            "confidence": 0.70
        }
        
        interpretation = clinical_interpreter.interpret_prediction(prediction)
        
        assert interpretation["urgency"] == "routine"
        assert len(interpretation["primary_findings"]) > 0
        assert len(interpretation["recommendations"]) > 0
        assert len(interpretation["differential_diagnosis"]) > 0
    
    def test_interpret_hyp(self):
        """Test interpretation of HYP prediction."""
        prediction = {
            "prediction": "Hypertrophy",
            "prediction_code": "HYP",
            "confidence": 0.80
        }
        
        interpretation = clinical_interpreter.interpret_prediction(prediction)
        
        assert interpretation["urgency"] == "routine"
        assert len(interpretation["primary_findings"]) > 0
        assert len(interpretation["recommendations"]) > 0
        assert len(interpretation["differential_diagnosis"]) > 0
    
    def test_interpret_with_features(self):
        """Test interpretation with extracted features."""
        prediction = {
            "prediction": "Myocardial Infarction",
            "prediction_code": "MI",
            "confidence": 0.85
        }
        
        features = {
            "temporal": {
                "II": {
                    "heart_rate": {"mean": 110, "std": 5},
                    "st_segment": {"elevation": 0.15, "depression": 0.05},
                    "qrs_features": {"duration": 0.08}
                }
            }
        }
        
        interpretation = clinical_interpreter.interpret_prediction(prediction, features)
        
        assert interpretation["urgency"] == "emergency"
        assert "feature_analysis" in interpretation
        assert len(interpretation["secondary_findings"]) >= 0  # May have additional findings
    
    def test_interpret_with_signal_quality(self):
        """Test interpretation with signal quality."""
        prediction = {
            "prediction": "Normal",
            "prediction_code": "NORM",
            "confidence": 0.90
        }
        
        interpretation = clinical_interpreter.interpret_prediction(prediction, signal_quality="poor")
        
        assert interpretation["signal_quality"] == "poor"
        assert any("signal quality" in lim.lower() for lim in interpretation["limitations"])
    
    def test_confidence_assessment(self):
        """Test confidence level assessment."""
        assert clinical_interpreter._assess_confidence(0.95) == "high"
        assert clinical_interpreter._assess_confidence(0.80) == "moderate"
        assert clinical_interpreter._assess_confidence(0.60) == "low"
        assert clinical_interpreter._assess_confidence(0.30) == "very_low"
    
    def test_clinical_significance_generation(self):
        """Test clinical significance generation."""
        interpretation = {
            "primary_findings": ["Test finding"],
            "urgency": "emergency",
            "prediction_context": {"confidence_level": "high"}
        }
        
        significance = clinical_interpreter._generate_clinical_significance("MI", 0.90, interpretation)
        
        assert "emergency" in significance.lower()
        assert "immediate" in significance.lower()
    
    def test_recommendations_generation(self):
        """Test recommendations generation."""
        recommendations = clinical_interpreter._generate_recommendations("MI", "emergency")
        
        assert len(recommendations) > 0
        assert any("emergency" in rec.lower() for rec in recommendations)
    
    def test_differential_diagnosis_generation(self):
        """Test differential diagnosis generation."""
        differential = clinical_interpreter._generate_differential_diagnosis("MI", None)
        
        assert len(differential) > 0
        assert "myocardial infarction" in " ".join(differential).lower()
    
    def test_standard_limitations(self):
        """Test standard limitations."""
        limitations = clinical_interpreter._get_standard_limitations()
        
        assert len(limitations) > 0
        assert any("healthcare professional" in lim.lower() for lim in limitations)
        assert any("research" in lim.lower() or "educational" in lim.lower() for lim in limitations)
    
    def test_interpretation_structure(self):
        """Test complete interpretation structure."""
        prediction = {
            "prediction": "Normal",
            "prediction_code": "NORM",
            "confidence": 0.90
        }
        
        interpretation = clinical_interpreter.interpret_prediction(prediction)
        
        # Check all required fields
        required_fields = [
            "primary_findings",
            "secondary_findings",
            "clinical_significance",
            "urgency",
            "recommendations",
            "differential_diagnosis",
            "limitations",
            "feature_analysis",
            "prediction_context"
        ]
        
        for field in required_fields:
            assert field in interpretation
        
        # Check prediction context
        assert interpretation["prediction_context"]["prediction"] == "Normal"
        assert interpretation["prediction_context"]["prediction_code"] == "NORM"
        assert interpretation["prediction_context"]["confidence"] == 0.90
        assert interpretation["prediction_context"]["confidence_level"] == "high"

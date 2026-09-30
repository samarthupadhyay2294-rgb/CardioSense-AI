"""
Tests for Safety Validator
"""

import pytest
from app.services.safety_validator import safety_validator


class TestSafetyValidator:
    """Test suite for safety validator."""
    
    def test_safe_language_passes(self):
        """Test that safe language passes validation."""
        response_dict = {
            "summary": "The model detected features possibly associated with myocardial infarction.",
            "primary_finding": "ECG patterns suggestive of myocardial infarction",
            "confidence_interpretation": "The model showed moderate confidence.",
            "possible_clinical_associations": [
                {
                    "name": "Coronary artery disease",
                    "explanation": "May be associated with coronary artery disease",
                    "relationship": "possible_association"
                }
            ],
            "why_flagged": "The model detected ST segment changes.",
            "what_it_means": "This may indicate possible ischemia.",
            "limitations": "ECG alone cannot establish diagnosis.",
            "disclaimer": "This is not a medical diagnosis."
        }
        
        # Should not raise an error
        validated = safety_validator.validate_response(response_dict)
        assert validated is not None
    
    def test_unsafe_language_detected_you_have(self):
        """Test that 'you have' pattern is detected."""
        response_dict = {
            "summary": "You have myocardial infarction.",
            "primary_finding": "Myocardial infarction",
            "confidence_interpretation": "High confidence",
            "possible_clinical_associations": [],
            "why_flagged": "ST elevation",
            "what_it_means": "You have a heart attack",
            "limitations": "None",
            "disclaimer": "Not a diagnosis"
        }
        
        with pytest.raises(ValueError) as exc_info:
            safety_validator.validate_response(response_dict)
        
        assert "unsafe diagnostic language" in str(exc_info.value).lower()
    
    def test_unsafe_language_detected_patient_has(self):
        """Test that 'the patient has' pattern is detected."""
        response_dict = {
            "summary": "The patient has heart disease.",
            "primary_finding": "Heart disease",
            "confidence_interpretation": "High confidence",
            "possible_clinical_associations": [],
            "why_flagged": "Abnormal rhythm",
            "what_it_means": "The patient has arrhythmia",
            "limitations": "None",
            "disclaimer": "Not a diagnosis"
        }
        
        with pytest.raises(ValueError) as exc_info:
            safety_validator.validate_response(response_dict)
        
        assert "unsafe diagnostic language" in str(exc_info.value).lower()
    
    def test_unsafe_language_detected_confirms(self):
        """Test that 'confirms' pattern is detected."""
        response_dict = {
            "summary": "This confirms myocardial infarction.",
            "primary_finding": "Myocardial infarction",
            "confidence_interpretation": "High confidence",
            "possible_clinical_associations": [],
            "why_flagged": "ST elevation",
            "what_it_means": "This confirms the diagnosis",
            "limitations": "None",
            "disclaimer": "Not a diagnosis"
        }
        
        with pytest.raises(ValueError) as exc_info:
            safety_validator.validate_response(response_dict)
        
        assert "unsafe diagnostic language" in str(exc_info.value).lower()
    
    def test_unsafe_language_in_association_name(self):
        """Test that unsafe language in association name is detected."""
        response_dict = {
            "summary": "The model detected abnormal patterns.",
            "primary_finding": "Abnormal ECG",
            "confidence_interpretation": "Moderate confidence",
            "possible_clinical_associations": [
                {
                    "name": "You definitely have heart disease",
                    "explanation": "This is confirmed",
                    "relationship": "possible_association"
                }
            ],
            "why_flagged": "Abnormal rhythm",
            "what_it_means": "Possible arrhythmia",
            "limitations": "ECG limitations",
            "disclaimer": "Not a diagnosis"
        }
        
        with pytest.raises(ValueError) as exc_info:
            safety_validator.validate_response(response_dict)
        
        assert "unsafe diagnostic language" in str(exc_info.value).lower()
    
    def test_unsafe_language_in_association_explanation(self):
        """Test that unsafe language in association explanation is detected."""
        response_dict = {
            "summary": "The model detected abnormal patterns.",
            "primary_finding": "Abnormal ECG",
            "confidence_interpretation": "Moderate confidence",
            "possible_clinical_associations": [
                {
                    "name": "Heart disease",
                    "explanation": "This confirms the patient has myocardial infarction",
                    "relationship": "possible_association"
                }
            ],
            "why_flagged": "Abnormal rhythm",
            "what_it_means": "Possible arrhythmia",
            "limitations": "ECG limitations",
            "disclaimer": "Not a diagnosis"
        }
        
        with pytest.raises(ValueError) as exc_info:
            safety_validator.validate_response(response_dict)
        
        assert "unsafe diagnostic language" in str(exc_info.value).lower()
    
    def test_transform_unsafe_language(self):
        """Test transformation of unsafe language."""
        unsafe_text = "You have myocardial infarction"
        transformed = safety_validator.transform_unsafe_language(unsafe_text)
        
        assert "you have" not in transformed.lower()
        assert "possibly associated with" in transformed.lower()
    
    def test_transform_patient_has(self):
        """Test transformation of 'the patient has'."""
        unsafe_text = "The patient has heart disease"
        transformed = safety_validator.transform_unsafe_language(unsafe_text)
        
        assert "the patient has" not in transformed.lower()
        assert "possibly associated with" in transformed.lower()
    
    def test_transform_confirms(self):
        """Test transformation of 'confirms'."""
        unsafe_text = "This confirms myocardial infarction"
        transformed = safety_validator.transform_unsafe_language(unsafe_text)
        
        assert "confirms" not in transformed.lower()
        assert "possible" in transformed.lower()
    
    def test_contains_safe_language(self):
        """Test detection of safe language patterns."""
        safe_text = "This may be associated with myocardial infarction"
        assert safety_validator.contains_safe_language(safe_text) is True
    
    def test_does_not_contain_safe_language(self):
        """Test when safe language is not present."""
        unsafe_text = "You have myocardial infarction"
        assert safety_validator.contains_safe_language(unsafe_text) is False
    
    def test_validate_associations_allowed(self):
        """Test validation of allowed associations."""
        associations = [
            {"name": "Coronary artery disease", "explanation": "May be associated", "relationship": "possible_association"},
            {"name": "Myocardial ischemia", "explanation": "Can be seen with", "relationship": "possible_association"}
        ]
        allowed = ["coronary artery disease", "myocardial ischemia", "heart disease"]
        
        result = safety_validator.validate_associations_allowed(associations, allowed)
        assert result is True
    
    def test_validate_associations_not_allowed(self):
        """Test rejection of disallowed associations."""
        associations = [
            {"name": "Coronary artery disease", "explanation": "May be associated", "relationship": "possible_association"},
            {"name": "Unrelated disease", "explanation": "Not in allowed list", "relationship": "possible_association"}
        ]
        allowed = ["coronary artery disease", "myocardial ischemia"]
        
        result = safety_validator.validate_associations_allowed(associations, allowed)
        assert result is False
    
    def test_multiple_unsafe_patterns(self):
        """Test detection of multiple unsafe patterns."""
        response_dict = {
            "summary": "You have myocardial infarction. This confirms the diagnosis.",
            "primary_finding": "Myocardial infarction",
            "confidence_interpretation": "High confidence",
            "possible_clinical_associations": [],
            "why_flagged": "ST elevation",
            "what_it_means": "The patient definitely has heart attack",
            "limitations": "None",
            "disclaimer": "Not a diagnosis"
        }
        
        with pytest.raises(ValueError) as exc_info:
            safety_validator.validate_response(response_dict)
        
        assert "unsafe diagnostic language" in str(exc_info.value).lower()

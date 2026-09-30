"""
Tests for Gemini Interpretation Service
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.gemini_service import (
    gemini_interpretation_service,
    GeminiConfigurationError,
    GeminiAPIError,
    InterpretationScope
)
from app.ml.prediction_normalizer import prediction_normalizer


class TestGeminiServiceConfiguration:
    """Test suite for Gemini service configuration."""
    
    def test_configuration_loads_from_settings(self):
        """Test that configuration loads from settings correctly."""
        # This test verifies the service can read configuration
        # Actual initialization is tested with mocked settings
        assert gemini_interpretation_service is not None
        assert gemini_interpretation_service.model_name is not None
    
    @patch('app.services.gemini_service.settings')
    def test_missing_api_key_raises_error(self, mock_settings):
        """Test that missing API key raises configuration error."""
        mock_settings.GEMINI_API_KEY = None
        mock_settings.GEMINI_MODEL = "gemini-2.0-flash-exp"
        
        service = gemini_interpretation_service.__class__()
        
        with pytest.raises(GeminiConfigurationError) as exc_info:
            service.initialize()
        
        assert "GEMINI_API_KEY is not configured" in str(exc_info.value)
        assert not service.is_available()
    
    @patch('app.services.gemini_service.settings')
    def test_api_key_present_initializes_successfully(self, mock_settings):
        """Test that valid API key allows initialization."""
        mock_settings.GEMINI_API_KEY = "test-api-key-12345"
        mock_settings.GEMINI_MODEL = "gemini-2.0-flash-exp"
        
        service = gemini_interpretation_service.__class__()
        
        # Mock the client initialization
        with patch.object(service, '_initialize_client'):
            service.initialize()
        
        assert service.is_available()
        assert service.api_key == "test-api-key-12345"
    
    def test_is_available_returns_false_when_not_initialized(self):
        """Test that is_available returns False before initialization."""
        service = gemini_interpretation_service.__class__()
        assert not service.is_available()
    
    def test_get_initialization_error_when_not_initialized(self):
        """Test getting initialization error when service is not initialized."""
        service = gemini_interpretation_service.__class__()
        error = service.get_initialization_error()
        assert error is None  # No error yet, just not initialized


class TestGeminiServiceInterpretation:
    """Test suite for Gemini interpretation functionality."""
    
    @patch('app.services.gemini_service.settings')
    def setup_service(self, mock_settings):
        """Helper to set up a mocked service for testing."""
        mock_settings.GEMINI_API_KEY = "test-api-key"
        mock_settings.GEMINI_MODEL = "gemini-2.0-flash-exp"
        
        service = gemini_interpretation_service.__class__()
        
        with patch.object(service, '_initialize_client'):
            service.initialize()
        
        return service
    
    def test_interpret_prediction_requires_initialization(self):
        """Test that interpretation fails when service is not initialized."""
        service = gemini_interpretation_service.__class__()
        
        normalized_prediction = {
            "input_type": "ecg_signal",
            "model": "ECGCNN",
            "primary_prediction": "Normal",
            "confidence": 0.85
        }
        
        with pytest.raises(GeminiConfigurationError) as exc_info:
            service.interpret_prediction(normalized_prediction)
        
        assert "not available" in str(exc_info.value)
    
    @patch('app.services.gemini_service.settings')
    def test_interpret_prediction_validates_input(self, mock_settings):
        """Test that interpretation validates input structure."""
        service = self.setup_service(mock_settings)
        
        # Missing required field
        invalid_prediction = {
            "input_type": "ecg_signal",
            "model": "ECGCNN"
            # Missing primary_prediction and confidence
        }
        
        with pytest.raises(ValueError) as exc_info:
            service.interpret_prediction(invalid_prediction)
        
        assert "Missing required field" in str(exc_info.value)
    
    @patch('app.services.gemini_service.settings')
    def test_interpret_prediction_validates_input_type(self, mock_settings):
        """Test that interpretation validates input_type field."""
        service = self.setup_service(mock_settings)
        
        invalid_prediction = {
            "input_type": "invalid_type",
            "model": "ECGCNN",
            "primary_prediction": "Normal",
            "confidence": 0.85
        }
        
        with pytest.raises(ValueError) as exc_info:
            service.interpret_prediction(invalid_prediction)
        
        assert "Invalid input_type" in str(exc_info.value)
    
    @patch('app.services.gemini_service.settings')
    def test_interpret_prediction_calls_gemini(self, mock_settings):
        """Test that interpretation calls Gemini API."""
        service = self.setup_service(mock_settings)
        
        normalized_prediction = {
            "input_type": "ecg_signal",
            "model": "ECGCNN",
            "primary_prediction": "Normal",
            "prediction_code": "NORM",
            "confidence": 0.85,
            "probabilities": {"Normal": 0.85},
            "existing_interpretation": {}
        }
        
        # Mock the Gemini call
        with patch.object(service, '_call_gemini', return_value={"text": "Test response"}):
            result = service.interpret_prediction(normalized_prediction)
        
        assert result is not None
        assert "safety_metadata" in result
    
    @patch('app.services.gemini_service.settings')
    def test_interpret_prediction_adds_safety_metadata(self, mock_settings):
        """Test that interpretation adds safety metadata."""
        service = self.setup_service(mock_settings)
        
        normalized_prediction = {
            "input_type": "ecg_signal",
            "model": "ECGCNN",
            "primary_prediction": "Normal",
            "prediction_code": "NORM",
            "confidence": 0.85,
            "probabilities": {"Normal": 0.85},
            "existing_interpretation": {}
        }
        
        with patch.object(service, '_call_gemini', return_value={"text": "Test response"}):
            result = service.interpret_prediction(normalized_prediction)
        
        assert "safety_metadata" in result
        assert result["safety_metadata"]["interpretation_scope"] == InterpretationScope.ECG_FINDING.value
        assert result["safety_metadata"]["system_type"] == "AI-assisted educational ECG screening"
        assert "disclaimer" in result["safety_metadata"]
    
    @patch('app.services.gemini_service.settings')
    def test_interpret_prediction_handles_api_failure(self, mock_settings):
        """Test that interpretation handles API failures gracefully."""
        service = self.setup_service(mock_settings)
        
        normalized_prediction = {
            "input_type": "ecg_signal",
            "model": "ECGCNN",
            "primary_prediction": "Normal",
            "prediction_code": "NORM",
            "confidence": 0.85,
            "probabilities": {"Normal": 0.85},
            "existing_interpretation": {}
        }
        
        # Mock API failure
        with patch.object(service, '_call_gemini', side_effect=Exception("API timeout")):
            with pytest.raises(GeminiAPIError) as exc_info:
                service.interpret_prediction(normalized_prediction)
        
        assert "Interpretation failed" in str(exc_info.value)


class TestGeminiServiceWithNormalizer:
    """Test suite for Gemini service integration with prediction normalizer."""
    
    @patch('app.services.gemini_service.settings')
    def test_end_to_end_signal_prediction(self, mock_settings):
        """Test end-to-end flow with signal prediction."""
        # Setup service
        mock_settings.GEMINI_API_KEY = "test-api-key"
        mock_settings.GEMINI_MODEL = "gemini-2.0-flash-exp"
        
        service = gemini_interpretation_service.__class__()
        with patch.object(service, '_initialize_client'):
            service.initialize()
        
        # Create raw prediction
        raw_prediction = {
            "prediction": "Myocardial Infarction",
            "prediction_code": "MI",
            "confidence": 0.92,
            "probabilities": {"Myocardial Infarction": 0.92},
            "all_predictions": {"Myocardial Infarction": True},
            "model_version": "1.0",
            "processing_time": 0.15
        }
        
        # Normalize
        normalized = prediction_normalizer.normalize_signal_prediction(raw_prediction)
        
        # Interpret
        with patch.object(service, '_call_gemini', return_value={"text": "Test interpretation"}):
            interpretation = service.interpret_prediction(normalized)
        
        assert interpretation is not None
        assert interpretation["safety_metadata"]["interpretation_scope"] == InterpretationScope.ECG_FINDING.value
    
    @patch('app.services.gemini_service.settings')
    def test_end_to_end_image_prediction(self, mock_settings):
        """Test end-to-end flow with image prediction."""
        # Setup service
        mock_settings.GEMINI_API_KEY = "test-api-key"
        mock_settings.GEMINI_MODEL = "gemini-2.0-flash-exp"
        
        service = gemini_interpretation_service.__class__()
        with patch.object(service, '_initialize_client'):
            service.initialize()
        
        # Create raw prediction
        raw_prediction = {
            "prediction": "N",
            "prediction_code": "N",
            "confidence": 0.78,
            "probabilities": {"N": 0.78},
            "model_name": "EfficientNet-B0",
            "model_version": "1.0",
            "processing_time": 0.089
        }
        
        # Normalize
        normalized = prediction_normalizer.normalize_image_prediction(raw_prediction)
        
        # Interpret
        with patch.object(service, '_call_gemini', return_value={"text": "Test interpretation"}):
            interpretation = service.interpret_prediction(normalized)
        
        assert interpretation is not None
        assert interpretation["safety_metadata"]["interpretation_scope"] == InterpretationScope.ECG_FINDING.value


class TestGeminiServiceSafety:
    """Test suite for Gemini service safety features."""
    
    @patch('app.services.gemini_service.settings')
    def setup_service(self, mock_settings):
        """Helper to set up a mocked service for testing."""
        mock_settings.GEMINI_API_KEY = "test-api-key"
        mock_settings.GEMINI_MODEL = "gemini-2.0-flash-exp"
        
        service = gemini_interpretation_service.__class__()
        
        with patch.object(service, '_initialize_client'):
            service.initialize()
        
        return service
    
    @patch('app.services.gemini_service.settings')
    def test_safety_disclaimer_content(self, mock_settings):
        """Test that safety disclaimer contains required elements."""
        service = self.setup_service(mock_settings)
        
        disclaimer = service._get_safety_disclaimer()
        
        assert "educational" in disclaimer.lower()
        assert "research" in disclaimer.lower()
        assert "NOT a medical diagnosis" in disclaimer
        assert "qualified healthcare professional" in disclaimer
    
    @patch('app.services.gemini_service.settings')
    def test_safety_settings_are_configured(self, mock_settings):
        """Test that safety settings are properly configured."""
        service = self.setup_service(mock_settings)
        
        safety_settings = service._get_safety_settings()
        
        assert safety_settings["block_hate_speech"] is True
        assert safety_settings["block_dangerous_content"] is True
        assert safety_settings["block_sexually_explicit"] is True
        assert safety_settings["block_harassment"] is True
    
    @patch('app.services.gemini_service.settings')
    def test_prompt_includes_safety_constraints(self, mock_settings):
        """Test that the prompt includes safety constraints."""
        service = self.setup_service(mock_settings)
        
        context = {
            "input_type": "ecg_signal",
            "model": "ECGCNN",
            "primary_prediction": "Normal",
            "prediction_code": "NORM",
            "confidence": 0.85,
            "probabilities": {"Normal": 0.85},
            "existing_interpretation": {}
        }
        
        prompt = service._build_safety_constrained_prompt(context)
        
        assert "NOT providing a medical diagnosis" in prompt
        assert "explain" in prompt.lower()
        assert "clinical associations" in prompt.lower()
        assert "confirmed diagnoses" in prompt.lower()

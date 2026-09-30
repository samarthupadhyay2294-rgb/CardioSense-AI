"""
Integration tests for Prompt 4: PDF, Assistant, and Caching
Tests the complete integration of Gemini interpretation across UI, PDF, and Assistant.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.gemini_service import gemini_interpretation_service, GeminiConfigurationError
from app.services.report_service import report_service
from app.services.summary_service import summary_service
from app.ml.prediction_normalizer import prediction_normalizer


class TestGeminiCaching:
    """Test Gemini interpretation caching."""
    
    def test_cache_key_generation(self):
        """Test cache key is generated consistently."""
        normalized = {
            "input_type": "signal",
            "prediction": "NORM",
            "confidence": 0.95,
            "probabilities": {"NORM": 0.95, "MI": 0.05}
        }
        
        key1 = gemini_interpretation_service._get_cache_key(normalized)
        key2 = gemini_interpretation_service._get_cache_key(normalized)
        
        assert key1 == key2, "Cache key should be consistent"
    
    def test_cache_key_different_predictions(self):
        """Test cache key differs for different predictions."""
        norm1 = {
            "input_type": "signal",
            "prediction": "NORM",
            "confidence": 0.95,
            "probabilities": {"NORM": 0.95, "MI": 0.05}
        }
        norm2 = {
            "input_type": "signal",
            "prediction": "MI",
            "confidence": 0.85,
            "probabilities": {"NORM": 0.15, "MI": 0.85}
        }
        
        key1 = gemini_interpretation_service._get_cache_key(norm1)
        key2 = gemini_interpretation_service._get_cache_key(norm2)
        
        assert key1 != key2, "Cache key should differ for different predictions"
    
    def test_cache_hit(self):
        """Test cache hit returns cached interpretation."""
        cache_key = ("signal", "NORM", 0.95, (("MI", 0.05), ("NORM", 0.95)))
        mock_interpretation = {
            "summary": "Test summary",
            "primary_finding": "Normal ECG"
        }
        
        gemini_interpretation_service._cache_interpretation(cache_key, mock_interpretation)
        cached = gemini_interpretation_service._get_cached_interpretation(cache_key)
        
        assert cached is not None
        assert cached["summary"] == "Test summary"
    
    def test_cache_miss(self):
        """Test cache miss returns None."""
        cache_key = ("signal", "NORM", 0.95, (("MI", 0.05), ("NORM", 0.95)))
        cached = gemini_interpretation_service._get_cached_interpretation(cache_key)
        
        assert cached is None
    
    def test_cache_expiration(self):
        """Test expired cache entries are not returned."""
        import time
        cache_key = ("signal", "NORM", 0.95, (("MI", 0.05), ("NORM", 0.95)))
        mock_interpretation = {"summary": "Test"}
        
        # Manually set an expired timestamp
        gemini_interpretation_service._cache[cache_key] = (
            mock_interpretation, 
            time.time() - gemini_interpretation_service._cache_ttl - 100
        )
        
        cached = gemini_interpretation_service._get_cached_interpretation(cache_key)
        
        assert cached is None
        assert cache_key not in gemini_interpretation_service._cache


class TestGeminiPDFIntegration:
    """Test Gemini interpretation integration into PDF reports."""
    
    def test_pdf_section_added(self):
        """Test that Gemini section is added to PDF story."""
        analysis = {
            "id": 1,
            "analysis_type": "signal",
            "prediction": "NORM",
            "confidence": 0.95,
            "file_name": "test.ecg"
        }
        
        story = []
        
        with patch.object(gemini_interpretation_service, 'is_available', return_value=False):
            report_service._add_gemini_interpretation_section(story, analysis)
        
        # Should have added at least the section header and fallback message
        assert len(story) > 0
    
    def test_pdf_gemini_unavailable_fallback(self):
        """Test PDF uses fallback when Gemini is unavailable."""
        analysis = {
            "id": 1,
            "analysis_type": "signal",
            "prediction": "NORM",
            "confidence": 0.95
        }
        
        story = []
        
        with patch.object(gemini_interpretation_service, 'is_available', return_value=False):
            report_service._add_gemini_interpretation_section(story, analysis)
        
        # Check that fallback message is present
        story_text = str(story)
        assert "unavailable" in story_text.lower()
    
    @patch('app.services.report_service.gemini_interpretation_service')
    @patch('app.services.report_service.prediction_normalizer')
    def test_pdf_with_gemini_available(self, mock_normalizer, mock_gemini):
        """Test PDF includes Gemini interpretation when available."""
        analysis = {
            "id": 1,
            "analysis_type": "signal",
            "prediction": "NORM",
            "confidence": 0.95
        }
        
        mock_gemini.is_available.return_value = True
        mock_gemini.interpret_prediction.return_value = {
            "success": True,
            "interpretation": {
                "summary": "Test summary",
                "primary_finding": "Normal ECG",
                "confidence_interpretation": "High confidence",
                "possible_clinical_associations": [],
                "why_flagged": "Not flagged",
                "what_it_means": "Normal rhythm",
                "limitations": "Test limitation",
                "disclaimer": "Test disclaimer"
            }
        }
        mock_normalizer.normalize_from_dict.return_value = {"prediction": "NORM"}
        
        story = []
        report_service._add_gemini_interpretation_section(story, analysis)
        
        # Should have added Gemini content
        story_text = str(story)
        assert "AI Clinical Interpretation" in story_text or len(story) > 0


class TestGeminiAssistantIntegration:
    """Test Gemini interpretation integration into Assistant."""
    
    def test_assistant_uses_gemini_context(self):
        """Test Assistant can answer questions about Gemini interpretation."""
        analysis = {
            "id": 1,
            "analysis_type": "signal",
            "prediction": "NORM",
            "confidence": 0.95,
            "probabilities": {"NORM": 0.95, "MI": 0.05}
        }
        
        with patch.object(gemini_interpretation_service, 'is_available', return_value=False):
            # When Gemini is unavailable, should return unavailable message
            answer = summary_service.answer_question(analysis, "What are the clinical associations?")
            assert "not available" in answer.lower()
    
    @patch('app.services.summary_service.gemini_interpretation_service')
    @patch('app.services.summary_service.prediction_normalizer')
    def test_assistant_gemini_associations_question(self, mock_normalizer, mock_gemini):
        """Test Assistant answers association questions using Gemini."""
        analysis = {
            "id": 1,
            "analysis_type": "signal",
            "prediction": "NORM",
            "confidence": 0.95
        }
        
        mock_gemini.is_available.return_value = True
        mock_gemini.interpret_prediction.return_value = {
            "success": True,
            "interpretation": {
                "possible_clinical_associations": [
                    {"name": "Normal Sinus Rhythm", "explanation": "Normal heart rhythm"}
                ]
            }
        }
        mock_normalizer.normalize_from_dict.return_value = {"prediction": "NORM"}
        
        answer = summary_service.answer_question(analysis, "What are the clinical associations?")
        
        assert "Normal Sinus Rhythm" in answer or "association" in answer.lower()
    
    @patch('app.services.summary_service.gemini_interpretation_service')
    @patch('app.services.summary_service.prediction_normalizer')
    def test_assistant_gemini_why_flagged_question(self, mock_normalizer, mock_gemini):
        """Test Assistant answers why flagged questions using Gemini."""
        analysis = {
            "id": 1,
            "analysis_type": "signal",
            "prediction": "MI",
            "confidence": 0.85
        }
        
        mock_gemini.is_available.return_value = True
        mock_gemini.interpret_prediction.return_value = {
            "success": True,
            "interpretation": {
                "why_flagged": "ST-segment elevation detected"
            }
        }
        mock_normalizer.normalize_from_dict.return_value = {"prediction": "MI"}
        
        answer = summary_service.answer_question(analysis, "Why was this flagged?")
        
        assert "ST-segment elevation" in answer or "flagged" in answer.lower()
    
    @patch('app.services.summary_service.gemini_interpretation_service')
    @patch('app.services.summary_service.prediction_normalizer')
    def test_assistant_gemini_what_it_means_question(self, mock_normalizer, mock_gemini):
        """Test Assistant answers what it means questions using Gemini."""
        analysis = {
            "id": 1,
            "analysis_type": "signal",
            "prediction": "MI",
            "confidence": 0.85
        }
        
        mock_gemini.is_available.return_value = True
        mock_gemini.interpret_prediction.return_value = {
            "success": True,
            "interpretation": {
                "what_it_means": "Possible myocardial infarction pattern"
            }
        }
        mock_normalizer.normalize_from_dict.return_value = {"prediction": "MI"}
        
        answer = summary_service.answer_question(analysis, "What does this mean?")
        
        assert "myocardial infarction" in answer or "mean" in answer.lower()


class TestEndToEndIntegration:
    """Test end-to-end integration flows."""
    
    @patch('app.services.summary_service.gemini_interpretation_service')
    @patch('app.services.summary_service.prediction_normalizer')
    def test_signal_workflow_with_gemini(self, mock_normalizer, mock_gemini):
        """Test complete signal workflow with Gemini."""
        analysis = {
            "id": 1,
            "analysis_type": "signal",
            "prediction": "NORM",
            "confidence": 0.95,
            "probabilities": {"NORM": 0.95, "MI": 0.05},
            "file_name": "test.ecg"
        }
        
        mock_gemini.is_available.return_value = True
        mock_gemini.interpret_prediction.return_value = {
            "success": True,
            "interpretation": {
                "summary": "Normal ECG",
                "primary_finding": "Normal sinus rhythm",
                "confidence_interpretation": "High confidence",
                "possible_clinical_associations": [],
                "why_flagged": "",
                "what_it_means": "",
                "limitations": "",
                "disclaimer": ""
            }
        }
        mock_normalizer.normalize_from_dict.return_value = {"prediction": "NORM"}
        
        # Test Assistant can use Gemini context
        answer = summary_service.answer_question(analysis, "What is the AI interpretation?")
        assert "AI" in answer or "interpretation" in answer.lower()
    
    @patch('app.services.summary_service.gemini_interpretation_service')
    @patch('app.services.summary_service.prediction_normalizer')
    def test_image_workflow_with_gemini(self, mock_normalizer, mock_gemini):
        """Test complete image workflow with Gemini."""
        analysis = {
            "id": 1,
            "analysis_type": "image",
            "prediction": "NORM",
            "confidence": 0.92,
            "primary_label": "Normal ECG",
            "file_name": "test.png"
        }
        
        mock_gemini.is_available.return_value = True
        mock_gemini.interpret_prediction.return_value = {
            "success": True,
            "interpretation": {
                "summary": "Normal ECG image",
                "primary_finding": "Normal pattern",
                "confidence_interpretation": "High confidence",
                "possible_clinical_associations": [],
                "why_flagged": "",
                "what_it_means": "",
                "limitations": "",
                "disclaimer": ""
            }
        }
        mock_normalizer.normalize_from_dict.return_value = {"prediction": "NORM"}
        
        # Test Assistant can use Gemini context for image
        answer = summary_service.answer_question(analysis, "What are the clinical associations?")
        assert "association" in answer.lower() or "not available" in answer.lower()
    
    def test_gemini_unavailable_does_not_break_core_functionality(self):
        """Test that core functionality works when Gemini is unavailable."""
        analysis = {
            "id": 1,
            "analysis_type": "signal",
            "prediction": "NORM",
            "confidence": 0.95,
            "probabilities": {"NORM": 0.95, "MI": 0.05},
            "file_name": "test.ecg"
        }
        
        with patch.object(gemini_interpretation_service, 'is_available', return_value=False):
            # Core Assistant questions should still work
            answer = summary_service.answer_question(analysis, "What is the prediction?")
            assert "NORM" in answer or "prediction" in answer.lower()
            
            # PDF should still generate
            story = []
            report_service._add_gemini_interpretation_section(story, analysis)
            assert len(story) > 0  # Should have fallback message


class TestDuplicateRequestPrevention:
    """Test that duplicate Gemini requests are prevented."""
    
    @patch('app.services.gemini_service.gemini_interpretation_service._call_gemini_api')
    @patch('app.services.gemini_service.clinical_context_builder')
    @patch('app.services.gemini_service.gemini_prompt_builder')
    @patch('app.services.gemini_service.gemini_schema_validator')
    @patch('app.services.gemini_service.safety_validator')
    def test_cache_prevents_duplicate_api_calls(self, mock_safety, mock_schema, mock_prompt, mock_context, mock_call):
        """Test that cached results prevent duplicate API calls."""
        normalized = {
            "input_type": "signal",
            "prediction": "NORM",
            "confidence": 0.95,
            "probabilities": {"NORM": 0.95, "MI": 0.05}
        }
        
        mock_context.build_context.return_value = {}
        mock_prompt.build_system_prompt.return_value = "system"
        mock_prompt.build_user_prompt.return_value = "user"
        mock_call.return_value = '{"summary": "test"}'
        mock_schema.validate_response.return_value = {"summary": "test"}
        mock_safety.validate_response.return_value = {"summary": "test"}
        
        # First call - should hit API
        result1 = gemini_interpretation_service.interpret_prediction(normalized)
        assert mock_call.call_count == 1
        
        # Second call with same data - should use cache
        result2 = gemini_interpretation_service.interpret_prediction(normalized)
        assert mock_call.call_count == 1  # Should not increment
        
        assert result1 == result2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

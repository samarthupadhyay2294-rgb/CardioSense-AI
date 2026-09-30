"""
Gemini Interpretation Service for CardioSense AI
Manages communication with Gemini API, prompt generation, schema validation, and caching.
"""

import hashlib
import json
import logging
from typing import Dict, Any, Optional

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from app.core.config import settings
from app.services.clinical_context import clinical_context_builder
from app.services.gemini_prompts import gemini_prompt_builder
from app.services.gemini_schemas import gemini_schema_validator
from app.services.safety_validator import safety_validator

logger = logging.getLogger(__name__)


class GeminiConfigurationError(Exception):
    """Raised when Gemini configuration is missing or invalid."""
    pass


class GeminiAPIError(Exception):
    """Raised when Gemini API call fails."""
    pass


from enum import Enum


class InterpretationScope(Enum):
    """Interpretation scope constants."""
    RESEARCH = "research"
    EDUCATIONAL = "educational"
    ECG_FINDING = "ecg_finding"


class GeminiInterpretationService:
    """Core service for generating LLM clinical interpretations via Gemini API."""

    def __init__(self):
        self.api_key = getattr(settings, "GEMINI_API_KEY", None)
        self.model_name = getattr(settings, "GEMINI_MODEL", "gemini-1.5-flash")
        self._initialized = False
        self._init_error = None
        self._cache = {}

    def _get_safety_disclaimer(self) -> str:
        """Return standardized safety disclaimer."""
        return (
            "This interpretation is provided for educational and research purposes only. "
            "It is NOT a medical diagnosis and does NOT replace evaluation by a qualified healthcare professional."
        )

    def _get_safety_settings(self) -> Dict[str, bool]:
        """Return safety filter settings."""
        return {
            "block_hate_speech": True,
            "block_dangerous_content": True,
            "block_sexually_explicit": True,
            "block_harassment": True,
        }

    def _initialize_client(self):
        """Initialize Google GenAI client."""
        if not self.api_key:
            raise GeminiConfigurationError("GEMINI_API_KEY is not configured")
        if genai is None:
            raise GeminiConfigurationError("google-generativeai package is not installed")
        genai.configure(api_key=self.api_key)

    def initialize(self):
        """Explicitly initialize the service."""
        try:
            self.api_key = getattr(settings, "GEMINI_API_KEY", None)
            self.model_name = getattr(settings, "GEMINI_MODEL", "gemini-1.5-flash")
            self._initialize_client()
            self._initialized = True
            self._init_error = None
        except Exception as e:
            self._initialized = False
            self._init_error = str(e)
            raise

    def is_available(self) -> bool:
        """Check if service is initialized and ready."""
        return self._initialized and bool(self.api_key)

    def get_initialization_error(self) -> Optional[str]:
        """Return initialization error message if any."""
        return self._init_error

    def _get_cache_key(self, normalized_prediction: Dict[str, Any]) -> str:
        """Generate a consistent cache key from prediction data."""
        key_data = {
            "input_type": normalized_prediction.get("input_type"),
            "prediction": normalized_prediction.get("primary_prediction"),
            "prediction_code": normalized_prediction.get("prediction_code"),
            "group": normalized_prediction.get("group"),
        }
        encoded = json.dumps(key_data, sort_keys=True).encode("utf-8")
        return hashlib.md5(encoded).hexdigest()

    def _call_gemini_api(self, system_prompt: str, user_prompt: str) -> str:
        """Call Gemini API model and return raw text output."""
        if not self.is_available():
            raise GeminiConfigurationError("Gemini service is not available")

        try:
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_prompt
            )
            response = model.generate_content(user_prompt)
            if hasattr(response, "text") and response.text:
                return response.text
            raise GeminiAPIError("Empty response returned from Gemini API")
        except Exception as e:
            if isinstance(e, (GeminiConfigurationError, GeminiAPIError)):
                raise
            raise GeminiAPIError(f"Gemini API call failed: {str(e)}")

    def _call_gemini(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Wrapper for _call_gemini_api returning parsed schema."""
        raw_text = self._call_gemini_api(system_prompt, user_prompt)
        return gemini_schema_validator.validate_response(raw_text)

    def interpret_prediction(self, normalized_prediction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate clinical interpretation for normalized prediction.
        Uses caching, context building, prompt building, schema validation, and safety validation.
        """
        if not self.is_available():
            raise GeminiConfigurationError("Gemini service is not available")

        cache_key = self._get_cache_key(normalized_prediction)
        if cache_key in self._cache:
            return self._cache[cache_key]

        context = clinical_context_builder.build_context(normalized_prediction)
        system_prompt = gemini_prompt_builder.build_system_prompt(context)
        user_prompt = gemini_prompt_builder.build_user_prompt(context)

        raw_text = self._call_gemini_api(system_prompt, user_prompt)
        parsed = gemini_schema_validator.validate_response(raw_text)
        validated = safety_validator.validate_response(parsed)
        if isinstance(validated, dict) and "safety_metadata" not in validated:
            validated["safety_metadata"] = {
                "interpretation_scope": InterpretationScope.ECG_FINDING.value,
                "non_diagnostic_disclaimer": self._get_safety_disclaimer(),
            }

        self._cache[cache_key] = validated
        return validated


gemini_interpretation_service = GeminiInterpretationService()

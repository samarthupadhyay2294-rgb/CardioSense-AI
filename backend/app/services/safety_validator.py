"""
Safety Validator for CardioSense AI
Enforces non-diagnostic language safety policies.
"""

from typing import Dict, Any, List, Union
import re


class SafetyValidator:
    """Post-processing safety validator to prevent definitive diagnostic claims."""

    UNSAFE_PATTERNS = [
        r"\byou have\b",
        r"\bthe patient has\b",
        r"\bthis confirms\b",
        r"\bthis proves\b",
        r"\bdefinitely has\b",
        r"\bdefinitely have\b",
        r"\bdefinitely is\b",
        r"\bdefinitely are\b",
        r"\bdiagnosed with\b",
        r"\bdefinitively\b",
        r"\byou are suffering from\b",
        r"\bthis ecg alone establishes\b",
    ]

    SAFE_PATTERNS = [
        "may be associated with",
        "can be seen in",
        "possible clinical association",
        "the model detected features associated with",
        "requires clinical correlation",
        "ecg finding alone does not establish",
    ]

    def contains_unsafe_language(self, text: str) -> bool:
        """Check if string contains any unsafe diagnostic patterns."""
        if not text or not isinstance(text, str):
            return False
        for pattern in self.UNSAFE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def contains_safe_language(self, text: str) -> bool:
        """Check if text uses approved non-diagnostic framing."""
        if not text or not isinstance(text, str):
            return False
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in self.SAFE_PATTERNS)

    def _check_value_recursive(self, value: Any):
        """Recursively check dictionary or list structure for unsafe language."""
        if isinstance(value, str):
            if self.contains_unsafe_language(value):
                raise ValueError(f"Response contains unsafe diagnostic language: '{value}'")
        elif isinstance(value, dict):
            for k, v in value.items():
                self._check_value_recursive(v)
        elif isinstance(value, list):
            for item in value:
                self._check_value_recursive(item)

    def validate_response(self, response_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Validate entire response object for safety compliance."""
        self._check_value_recursive(response_dict)
        return response_dict

    def transform_unsafe_language(self, text: str) -> str:
        """Replace unsafe phrases with conservative framing."""
        if not text:
            return text
        result = text
        result = re.sub(r"\byou have\b", "possibly associated with", result, flags=re.IGNORECASE)
        result = re.sub(r"\bthe patient has\b", "possibly associated with", result, flags=re.IGNORECASE)
        result = re.sub(r"\bthis confirms\b", "possible", result, flags=re.IGNORECASE)
        result = re.sub(r"\bthis proves\b", "possible", result, flags=re.IGNORECASE)
        result = re.sub(r"\bdefinitely\b", "possibly", result, flags=re.IGNORECASE)
        return result

    def validate_associations_allowed(
        self, associations: List[Union[Dict, str]], allowed: List[str]
    ) -> bool:
        """Validate that all clinical associations match the allowed controlled list."""
        if not allowed:
            return True
        allowed_lower = {a.lower() for a in allowed}
        for assoc in associations:
            name = assoc if isinstance(assoc, str) else assoc.get("name", "")
            if not any(a_low in name.lower() for a_low in allowed_lower):
                return False
        return True


safety_validator = SafetyValidator()

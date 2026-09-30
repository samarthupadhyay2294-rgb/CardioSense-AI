"""
Gemini Schemas & Validator for CardioSense AI
Parses and validates JSON and text-based responses from Gemini, ensuring consistent fields.
"""

import json
import logging
import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class GeminiInterpretationTextResponse(BaseModel):
    """Pydantic model for parsed response structure."""
    summary: str
    primary_finding: str
    interpretation_confidence: str
    possible_clinical_associations: List[Dict[str, str]]


class GeminiSchemaValidator:
    """Validates and parses structured JSON/text response from Gemini."""

    VALID_CONFIDENCES = {"high", "moderate", "low"}

    def validate_response(self, raw_text: str) -> Dict[str, Any]:
        """
        Parse structured text or JSON response into dictionary format.
        Ensures summary, primary_finding, interpretation_confidence, and possible_clinical_associations exist.
        """
        if not raw_text or not isinstance(raw_text, str):
            raise ValueError("Invalid response from Gemini API: Empty or non-string response")

        text = raw_text.strip()
        
        # Log response structure for debugging (NEVER LOG API KEY)
        logger.info(f"[GEMINI RESPONSE PARSER] Raw response length: {len(text)}, prefix snippet: {text[:150]!r}")

        # Unwrap markdown code fences if present
        if "```" in text:
            match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", text, re.DOTALL | re.IGNORECASE)
            if match:
                text = match.group(1).strip()

        data = None

        # Try parsing JSON
        if text.startswith("{") and text.endswith("}"):
            try:
                data = json.loads(text)
            except json.JSONDecodeError as e:
                logger.warning(f"[GEMINI RESPONSE PARSER] Direct JSON load failed: {e}. Attempting clean loading.")
                cleaned = re.sub(r",\s*([}\]])", r"\1", text)
                try:
                    data = json.loads(cleaned)
                except Exception:
                    data = None

        # Fallback to text format parser if not JSON
        if not data:
            data = self._parse_text_format(text)

        summary = data.get("summary") or ""
        primary_finding = data.get("primary_finding") or data.get("finding") or ""
        
        confidence = (
            data.get("interpretation_confidence")
            or data.get("confidence_interpretation")
            or data.get("confidence")
            or "Moderate"
        )
        if isinstance(confidence, str):
            clean_c = re.sub(r"[^\w]", "", confidence).capitalize()
            if clean_c.lower() in self.VALID_CONFIDENCES:
                confidence = clean_c
            else:
                confidence = "Moderate"
        else:
            confidence = "Moderate"

        raw_assoc = data.get("possible_clinical_associations") or []
        normalized_assoc: List[Dict[str, str]] = []

        if isinstance(raw_assoc, list):
            for item in raw_assoc:
                if isinstance(item, dict):
                    name = item.get("name") or item.get("condition") or item.get("title") or "Clinical Association"
                    explanation = item.get("explanation") or item.get("description") or item.get("details") or name
                    normalized_assoc.append({"name": str(name), "explanation": str(explanation)})
                elif isinstance(item, str) and item.strip():
                    clean_item = item.strip()
                    if ":" in clean_item:
                        parts = clean_item.split(":", 1)
                        normalized_assoc.append({"name": parts[0].strip(), "explanation": parts[1].strip()})
                    elif " - " in clean_item:
                        parts = clean_item.split(" - ", 1)
                        normalized_assoc.append({"name": parts[0].strip(), "explanation": parts[1].strip()})
                    else:
                        normalized_assoc.append({"name": clean_item, "explanation": clean_item})

        # Ensure summary or primary_finding is populated
        if not summary and not primary_finding:
            raise ValueError("Gemini response missing essential summary and primary_finding content")

        if not summary:
            summary = primary_finding
        if not primary_finding:
            primary_finding = summary

        result = {
            "summary": summary,
            "primary_finding": primary_finding,
            "interpretation_confidence": confidence,
            "confidence_interpretation": confidence,
            "possible_clinical_associations": normalized_assoc,
            "why_flagged": data.get("why_flagged") or "",
            "what_it_means": data.get("what_it_means") or "",
            "limitations": data.get("limitations") or "Single ECG observation without clinical correlation.",
            "disclaimer": data.get("disclaimer") or "This interpretation is generated by CardioSense AI for educational and decision-support purposes only and does not constitute a medical diagnosis."
        }

        logger.info(f"[GEMINI RESPONSE PARSER] Parsed successfully: summary_len={len(summary)}, assoc_count={len(normalized_assoc)}")
        return result

    def _parse_text_format(self, text: str) -> Dict[str, Any]:
        """Fallback parser for text-based section formats."""
        summary = ""
        primary_finding = ""
        confidence = "Moderate"
        associations = []

        sum_m = re.search(r"Summary:\s*\n?([^\n]+(?:\n(?!Primary Finding:)[^\n]+)*)", text, re.IGNORECASE)
        if sum_m:
            summary = sum_m.group(1).strip()

        prim_m = re.search(r"Primary Finding:\s*\n?([^\n]+(?:\n(?!Interpretation Confidence:)[^\n]+)*)", text, re.IGNORECASE)
        if prim_m:
            primary_finding = prim_m.group(1).strip()

        conf_m = re.search(r"Interpretation Confidence:\s*\n?([^\n]+)", text, re.IGNORECASE)
        if conf_m:
            confidence = conf_m.group(1).strip()

        assoc_m = re.search(r"Possible Clinical Associations:\s*\n?(.*)", text, re.IGNORECASE | re.DOTALL)
        if assoc_m:
            assoc_block = assoc_m.group(1).strip()
            for line in assoc_block.split("\n"):
                line = line.strip()
                if line.startswith("-") or line.startswith("*") or re.match(r"^\d+\.", line):
                    item = re.sub(r"^[-*\d\.\s]+", "", line).strip()
                    if item:
                        associations.append(item)

        return {
            "summary": summary,
            "primary_finding": primary_finding,
            "interpretation_confidence": confidence,
            "possible_clinical_associations": associations,
        }


gemini_schema_validator = GeminiSchemaValidator()

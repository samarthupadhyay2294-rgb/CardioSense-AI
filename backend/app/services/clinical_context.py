"""
Clinical Context Builder for CardioSense AI
Builds controlled clinical context for Gemini interpretation.
"""

from typing import Dict, Any, List, Optional


class ClinicalContextBuilder:
    """Builds controlled clinical context for LLM prompt construction."""

    SIGNAL_ASSOCIATIONS = {
        "NORM": [
            "Normal cardiac electrical activity",
            "Unremarkable ECG findings",
            "Baseline physiological state",
        ],
        "MI": [
            "Myocardial ischemia or infarction",
            "Coronary artery disease",
            "Myocardial injury",
        ],
        "STTC": [
            "Myocardial ischemia",
            "Electrolyte imbalances",
            "Ventricular strain or repolarization abnormality",
        ],
        "CD": [
            "Intraventricular conduction delay or block",
            "Bundle branch block",
            "Conduction system disease",
        ],
        "HYP": [
            "Left or right ventricular hypertrophy",
            "Systemic hypertension",
            "Valvular heart disease",
        ],
    }

    IMAGE_ASSOCIATIONS = {
        "N": [
            "Normal beat pattern",
            "Physiological cardiac impulse",
        ],
        "L": [
            "Left bundle branch block pattern",
            "Intraventricular conduction delay",
        ],
        "R": [
            "Right bundle branch block pattern",
            "Right ventricular conduction delay",
        ],
        "V": [
            "Ventricular premature beat (PVC)",
            "Ectopic ventricular focus",
        ],
        "A": [
            "Atrial premature beat (PAC)",
            "Ectopic atrial focus",
        ],
    }

    IMAGE_GROUP_ASSOCIATIONS = {
        "Normal": ["Normal rhythm pattern"],
        "Ventricular": ["Ectopic ventricular activity or ventricular conduction pattern"],
        "Supraventricular": ["Atrial or AV nodal pattern"],
    }

    def _assess_confidence_level(self, confidence: float) -> str:
        """Internal helper to categorize confidence."""
        if confidence >= 0.80:
            return "high"
        elif confidence >= 0.60:
            return "moderate"
        elif confidence >= 0.40:
            return "low"
        return "very_low"

    def build_context(
        self, normalized_prediction: Dict[str, Any], include_confidence: bool = False
    ) -> Dict[str, Any]:
        """Build controlled clinical context without model confidence scores by default."""
        input_type = normalized_prediction.get("input_type")
        if input_type not in ("ecg_signal", "ecg_image"):
            raise ValueError(f"Unsupported input_type: {input_type}")

        prediction_code = normalized_prediction.get("prediction_code", "NORM")
        primary_pred = normalized_prediction.get("primary_prediction", "N/A")

        if input_type == "ecg_signal":
            associations = self.SIGNAL_ASSOCIATIONS.get(
                prediction_code, ["Possible non-specific ECG pattern"]
            )
            ecg_finding = f"{primary_pred} ({prediction_code})" if prediction_code != "NORM" else "Normal sinus rhythm"
            group = None
        else:
            associations = self.IMAGE_ASSOCIATIONS.get(
                prediction_code, ["Possible non-specific ECG pattern"]
            )
            group = normalized_prediction.get("group")
            if group and group in self.IMAGE_GROUP_ASSOCIATIONS:
                associations = list(set(associations + self.IMAGE_GROUP_ASSOCIATIONS[group]))
            ecg_finding = f"{primary_pred} ({prediction_code})"

        ctx = {
            "input_type": input_type,
            "model": normalized_prediction.get("model", "CardioSense Model"),
            "primary_prediction": primary_pred,
            "prediction_code": prediction_code,
            "group": group,
            "ecg_finding": ecg_finding,
            "possible_associations": associations,
            "limitations": [
                "Single ECG observation without clinical correlation",
                "Requires evaluation by a qualified healthcare professional",
            ],
            "safety_instructions": [
                "Explain ECG finding without diagnosing",
                "Do NOT use model confidence or percentages",
                "Determine interpretation confidence from clinical evidence",
            ],
            "non_diagnostic_requirement": True,
        }

        if include_confidence:
            confidence = normalized_prediction.get("confidence", 0.0)
            ctx["confidence"] = confidence
            ctx["confidence_level"] = self._assess_confidence_level(confidence)

        return ctx


clinical_context_builder = ClinicalContextBuilder()

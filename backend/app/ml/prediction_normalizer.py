"""
Prediction Normalizer for CardioSense AI
Normalizes signal and image prediction results into a standard structure.
"""

from typing import Dict, Any, Optional, List


class PredictionNormalizer:
    """Normalizes prediction results across signal and image models."""

    def normalize_signal_prediction(
        self,
        prediction_result: Dict[str, Any],
        detailed_features: Optional[Dict[str, Any]] = None,
        signal_quality: Optional[str] = None,
        clinical_interpretation: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Normalize signal prediction result."""
        return {
            "input_type": "ecg_signal",
            "model": prediction_result.get("model_version", "1.0"),
            "primary_prediction": prediction_result.get("prediction", "N/A"),
            "prediction_code": prediction_result.get("prediction_code", "NORM"),
            "confidence": prediction_result.get("confidence", 0.0),
            "probabilities": prediction_result.get("probabilities", {}),
            "all_predictions": prediction_result.get("all_predictions", {}),
            "model_metadata": {
                "model_version": prediction_result.get("model_version", "1.0"),
                "processing_time": prediction_result.get("processing_time", 0.0),
            },
            "existing_interpretation": {
                "detailed_features": detailed_features,
                "signal_quality": signal_quality,
                "clinical_interpretation": clinical_interpretation,
            },
        }

    def normalize_image_prediction(
        self,
        prediction_result: Dict[str, Any],
        interpretation: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Normalize image prediction result."""
        interp = interpretation or {}
        return {
            "input_type": "ecg_image",
            "model": prediction_result.get("model_name", "EfficientNet-B0"),
            "primary_prediction": prediction_result.get("prediction", "N/A"),
            "prediction_code": prediction_result.get("prediction_code", "N"),
            "confidence": prediction_result.get("confidence", 0.0),
            "probabilities": prediction_result.get("probabilities", {}),
            "group": interp.get("dominant_group", prediction_result.get("dominant_group")),
            "group_probabilities": interp.get("group_probabilities", prediction_result.get("group_probabilities", {})),
            "subclass_results": interp.get("subclass_results", prediction_result.get("subclass_results", [])),
            "pattern_summary": interp.get("pattern_summary", prediction_result.get("pattern_summary")),
            "recommended_next_steps": interp.get("recommended_next_steps", prediction_result.get("recommended_next_steps", [])),
            "model_metadata": {
                "model_name": prediction_result.get("model_name", "EfficientNet-B0"),
                "model_version": prediction_result.get("model_version", "1.0"),
                "processing_time": prediction_result.get("processing_time", 0.0),
            },
            "existing_interpretation": {
                "detailed_features": None,
                "signal_quality": None,
                "clinical_interpretation": None,
            },
        }

    def normalize_from_analysis_dict(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize from database analysis dictionary."""
        analysis_type = analysis.get("analysis_type", "signal")
        if analysis_type == "image":
            return self.normalize_image_prediction(analysis, interpretation=analysis)
        return self.normalize_signal_prediction(
            analysis,
            detailed_features=analysis.get("detailed_features"),
            signal_quality=analysis.get("signal_quality"),
            clinical_interpretation=analysis.get("clinical_interpretation"),
        )


prediction_normalizer = PredictionNormalizer()

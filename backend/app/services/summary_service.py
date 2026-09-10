from typing import Dict, Any
import re


class SummaryService:
    def __init__(self):
        self.class_descriptions = {}

    def set_class_descriptions(self, descriptions: Dict[str, str]):
        self.class_descriptions = descriptions

    def generate_summary(self, analysis: Dict[str, Any]) -> str:
        prediction = analysis.get("prediction", "N/A")
        confidence = analysis.get("confidence", 0)
        probabilities = analysis.get("probabilities", {})
        signal_quality = analysis.get("signal_quality", "N/A")
        num_leads = analysis.get("num_leads", "N/A")
        sampling_rate = analysis.get("sampling_rate", "N/A")
        duration = analysis.get("duration", "N/A")
        all_predictions = analysis.get("all_predictions", {})
        model_name = analysis.get("model_name", "ECGCNN")
        is_image = analysis.get("analysis_type") == "image"

        confidence_level = (
            "high" if confidence >= 0.8
            else "moderate" if confidence >= 0.6
            else "low"
        )

        if is_image:
            subclass_results = analysis.get("subclass_results") or []
            group_probs = analysis.get("group_probabilities") or {}
            dominant_group = analysis.get("dominant_group") or "Unknown"

            if subclass_results:
                top = subclass_results[0]
                primary_text = (
                    f"The primary class is {top['human_readable_label']} (class {top['raw_class']}) "
                    f"with {confidence_level} model confidence ({confidence * 100:.1f}%)."
                )
            else:
                primary_text = (
                    f"The primary class is {prediction} with {confidence_level} model confidence "
                    f"({confidence * 100:.1f}%)."
                )

            summary_parts = [
                f"The ECG image was analyzed by CardioSense AI ({model_name} version {analysis.get('model_version', '1.0')}). "
                + primary_text
            ]

            if group_probs:
                dom_desc = ", ".join(
                    f"{g} {p * 100:.1f}%" for g, p in group_probs.items()
                )
                summary_parts.append(
                    f"The dominant higher-level ECG group is {dominant_group}. "
                    f"Group probability distribution: {dom_desc}."
                )

            if subclass_results:
                top_probs = subclass_results[:3]
                probs_text = "; ".join(
                    f"{r['human_readable_label']} at {r['probability'] * 100:.1f}%"
                    for r in top_probs
                )
                summary_parts.append(f"The highest model probabilities were {probs_text}.")

            summary_parts.append(
                "Model confidence reflects how strongly the trained model matches the image to each "
                "class; it is not a clinically calibrated probability and is not a disease or risk "
                "probability."
            )

            grad = "Grad-CAM visualization is available for this analysis." if analysis.get("gradcam_available") else "Grad-CAM is not available for this analysis."
            summary_parts.append(grad)

            summary_parts.append(
                "This summary is generated from the model output and image data only. It is not a "
                "medical diagnosis and does not replace evaluation by a qualified healthcare "
                "professional."
            )
            return " ".join(summary_parts)

        detected = [cls for cls, pred in all_predictions.items() if pred]
        if not detected:
            detected_text = "no abnormal findings"
        else:
            detected_text = ", ".join(detected)

        summary_parts = [
            f"The ECG signal was analyzed by CardioSense AI (model {analysis.get('model_version', '1.0')}). "
            f"The primary finding is {prediction} with {confidence_level} confidence ({confidence * 100:.1f}%)."
        ]

        if all_predictions:
            summary_parts.append(
                f"Across all categories, the model indicates the following: {detected_text}."
            )

        if probabilities:
            top_probs = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)[:2]
            probs_text = "; ".join(f"{cls} at {prob * 100:.1f}%" for cls, prob in top_probs)
            summary_parts.append(f"The highest model probabilities were {probs_text}.")

        summary_parts.append(
            f"The signal spans {duration:.1f} seconds across {num_leads} leads at {sampling_rate} Hz "
            f"with {signal_quality} signal quality."
        )

        description = self.class_descriptions.get(prediction)
        if description:
            summary_parts.append(f"Description: {description}")

        summary_parts.append(
            "This summary is generated from the model output and technical signal data only. "
            "It is not a medical diagnosis and does not replace evaluation by a qualified healthcare professional."
        )

        return " ".join(summary_parts)

    def answer_question(self, analysis: Dict[str, Any], question: str) -> str:
        question = question.lower().strip()
        is_image = analysis.get("analysis_type") == "image"

        if any(word in question for word in ["shape", "input", "size", "resolution", "dimension"]):
            if is_image:
                return (
                    f"This ECG image analysis used the EfficientNet-B0 model. Images are converted to RGB, "
                    f"resized to 244x244 and center-cropped to 224x224, then normalized with ImageNet statistics "
                    f"(mean {[round(m, 3) for m in [0.485, 0.456, 0.406]]}, std {[round(s, 3) for s in [0.229, 0.224, 0.225]]})."
                )
            return (
                f"This ECG signal has {analysis.get('num_leads', 'N/A')} leads sampled at "
                f"{analysis.get('sampling_rate', 'N/A')} Hz over {analysis.get('duration', 'N/A'):.1f} seconds, "
                f"normalized with per-record z-score."
            )

        if any(word in question for word in ["gradcam", "heatmap", "explain", "why", "important", "region", "overlay"]):
            if is_image:
                if analysis.get("gradcam_available"):
                    return (
                        "Grad-CAM was computed for this ECG image. It highlights the image regions the model found "
                        "most influential for its prediction. Grad-CAM shows influential image regions only; it does "
                        "not constitute a clinical finding."
                    )
                return "Grad-CAM is not available for this image analysis."
            explainability = analysis.get("explainability")
            if explainability and "error" not in explainability:
                leads = explainability.get("lead_importance", {})
                top_leads = sorted(leads.items(), key=lambda x: x[1], reverse=True)[:3]
                lead_text = ", ".join(f"{lead} ({imp * 100:.1f}%)" for lead, imp in top_leads)
                return (
                    f"The explainability analysis (Integrated Gradients) identified these leads as most influential "
                    f"for the prediction: {lead_text}. Highlighted regions represent signal areas that contributed to "
                    f"the model prediction; they should not be interpreted as a clinical diagnosis."
                )
            return "Explainability data is not available for this analysis."

        if any(word in question for word in ["model", "version", "what model", "architecture"]):
            if is_image:
                return (
                    f"This analysis used the {analysis.get('model_name', 'EfficientNet-B0')} image model "
                    f"(version {analysis.get('model_version', '1.0')}), a ImageNet-pretrained EfficientNet-B0 "
                    f"transfer-learned for 15 ECG image classes (A, E, F, J, L, N, Q, R, S, V, aa, e, f, j, p)."
                )
            return (
                f"This analysis was performed using CardioSense AI model version {analysis.get('model_version', '1.0')}, "
                f"a 1D convolutional neural network (ECGCNN) with 4 convolutional blocks and approximately 339K parameters, "
                f"trained on the PTB-XL dataset."
            )

        if any(word in question for word in ["confidence", "sure", "certain", "probability", "probable"]):
            if is_image:
                group_probs = analysis.get("group_probabilities") or {}
                group_text = "; ".join(
                    f"{g} {p * 100:.1f}%"
                    for g, p in sorted(group_probs.items(), key=lambda x: -x[1])
                )
                return (
                    f"The model assigned a confidence of {analysis.get('confidence', 0) * 100:.1f}% to the "
                    f"primary subclass {analysis.get('primary_label', analysis.get('prediction', 'N/A'))}. "
                    f"Higher-level ECG group probabilities: {group_text or 'N/A'}. These values are model "
                    f"pattern similarities, not disease probabilities."
                )
            return (
                f"The model assigned a confidence of {analysis.get('confidence', 0) * 100:.1f}% to the primary "
                f"finding of {analysis.get('prediction', 'N/A')}. "
                f"Full probabilities are: "
                + "; ".join(f"{cls} {prob * 100:.1f}%" for cls, prob in analysis.get("probabilities", {}).items())
            )

        if any(word in question for word in ["lead", "channel"]):
            return (
                f"This ECG recording contains {analysis.get('num_leads', 'N/A')} leads "
                f"sampled at {analysis.get('sampling_rate', 'N/A')} Hz over "
                f"{analysis.get('duration', 'N/A'):.1f} seconds."
            )

        if any(word in question for word in ["quality", "signal", "noise"]):
            if is_image:
                return (
                    f"This is an ECG image analysis, so there is no numerical signal-quality metric. The model "
                    f"processed the uploaded image with the training-compatible preprocessing (RGB, resize, "
                    f"center-crop, ImageNet normalization)."
                )
            return (
                f"The signal quality was assessed as {analysis.get('signal_quality', 'N/A')}. "
                f"This reflects the general noise level and amplitude characteristics of the recording."
            )

        if any(word in question for word in ["result", "predict", "find", "diagnos", "abnormal", "what did"]):
            if is_image:
                subclass_results = analysis.get("subclass_results") or []
                top = subclass_results[:3]
                top_text = "; ".join(
                    f"{r['human_readable_label']} ({r['raw_class']}) {r['probability'] * 100:.1f}%"
                    for r in top
                ) if top else (
                    "; ".join(
                        f"{cls} {prob * 100:.1f}%"
                        for cls, prob in sorted(
                            analysis.get("probabilities", {}).items(), key=lambda x: -x[1]
                        )[:3]
                    )
                )
                return (
                    f"The primary class predicted by the image model is "
                    f"{analysis.get('primary_label', analysis.get('prediction', 'N/A'))} "
                    f"with {analysis.get('confidence', 0) * 100:.1f}% model confidence. "
                    f"The dominant higher-level ECG group is "
                    f"{analysis.get('dominant_group', 'Unknown')}. Top subclasses: {top_text}. "
                    f"This is a model pattern assessment, not a diagnosis."
                )
            return (
                f"The primary finding is {analysis.get('prediction', 'N/A')} "
                f"with {analysis.get('confidence', 0) * 100:.1f}% confidence. "
                f"Detected categories: "
                + ", ".join(cls for cls, pred in analysis.get("all_predictions", {}).items() if pred)
                or "none"
            )

        if any(word in question for word in ["time", "how long", "speed", "processing"]):
            return (
                f"The analysis took approximately {analysis.get('processing_time', 'N/A'):.3f} seconds "
                f"on {analysis.get('model_version', 'N/A')}."
            )

        if any(word in question for word in ["stat", "measure", "amplitude", "heart rate"]):
            stats = analysis.get("ecg_statistics", {}).get("overall", {})
            return (
                f"Signal statistics: mean amplitude {stats.get('mean_amplitude', 'N/A'):.4f}, "
                f"max amplitude {stats.get('max_amplitude', 'N/A'):.4f}, "
                f"signal length {stats.get('signal_length', 'N/A')} samples across "
                f"{stats.get('num_leads', 'N/A')} leads."
            )

        if any(word in question for word in ["explain", "why", "attention", "important"]):
            explainability = analysis.get("explainability")
            if explainability and "error" not in explainability:
                leads = explainability.get("lead_importance", {})
                top_leads = sorted(leads.items(), key=lambda x: x[1], reverse=True)[:3]
                lead_text = ", ".join(f"{lead} ({imp * 100:.1f}%)" for lead, imp in top_leads)
                return (
                    f"The explainability analysis (Integrated Gradients) identified these leads as most influential "
                    f"for the prediction: {lead_text}. Highlighted regions represent signal areas that contributed to "
                    f"the model prediction; they should not be interpreted as a clinical diagnosis."
                )
            return "Explainability data is not available for this analysis."

        if any(word in question for word in ["file", "name", "upload"]):
            return f"The analyzed file was named '{analysis.get('file_name', 'N/A')}'."

        return (
            "I can answer questions about this ECG analysis: the prediction and confidence, "
            "model probabilities, signal statistics and quality, leads and sampling, processing time, "
            "explainability, or the file analyzed. I use only data from this analysis and do not provide medical diagnosis."
        )


summary_service = SummaryService()
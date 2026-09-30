"""
Test script for new Gemini interpretation prompt structure.
This tests the updated prompt that removes model confidence and uses text format.
"""

from app.services.gemini_prompts import gemini_prompt_builder
from app.services.clinical_context import clinical_context_builder
from app.ml.prediction_normalizer import prediction_normalizer

# Test with a sample signal prediction
raw_prediction = {
    "prediction": "Myocardial Infarction",
    "prediction_code": "MI",
    "confidence": 0.92,
    "probabilities": {"Myocardial Infarction": 0.92, "Normal": 0.05, "STTC": 0.02, "CD": 0.01, "HYP": 0.00},
    "all_predictions": {"Myocardial Infarction": True},
    "model_version": "1.0",
    "processing_time": 0.15
}

# Normalize the prediction
normalized = prediction_normalizer.normalize_signal_prediction(raw_prediction)

# Build clinical context
clinical_context = clinical_context_builder.build_context(normalized)

# Build prompts
system_prompt = gemini_prompt_builder.build_system_prompt(clinical_context)
user_prompt = gemini_prompt_builder.build_user_prompt(clinical_context)

print("=" * 80)
print("SYSTEM PROMPT:")
print("=" * 80)
print(system_prompt)
print("\n")

print("=" * 80)
print("USER PROMPT:")
print("=" * 80)
print(user_prompt)
print("\n")

# Verify confidence is not in the context
assert "confidence" not in clinical_context or clinical_context.get("confidence") is None, "Confidence should not be in clinical context"
assert "confidence_level" not in clinical_context, "Confidence level should not be in clinical context"

print("[OK] Confidence successfully removed from clinical context")
print("[OK] New prompt structure generated successfully")

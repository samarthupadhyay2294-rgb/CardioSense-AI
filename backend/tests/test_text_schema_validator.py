"""
Test script for new text-based schema validator.
This tests parsing the new text format response.
"""

from app.services.gemini_schemas import gemini_schema_validator

# Sample response in the new text format
sample_response = """Summary:
The ECG shows patterns that may indicate myocardial infarction, which requires clinical correlation.

Primary Finding:
ECG patterns suggestive of myocardial infarction (heart attack)

Interpretation Confidence:
Moderate

Possible Clinical Associations:
- May be associated with coronary artery disease
- Can be seen with acute myocardial ischemia
- Possible association with previous myocardial injury"""

print("=" * 80)
print("SAMPLE RESPONSE:")
print("=" * 80)
print(sample_response)
print("\n")

# Parse and validate
try:
    parsed = gemini_schema_validator.validate_response(sample_response)

    print("=" * 80)
    print("PARSED RESPONSE:")
    print("=" * 80)
    print(f"Summary: {parsed.get('summary')}")
    print(f"Primary Finding: {parsed.get('primary_finding')}")
    print(f"Interpretation Confidence: {parsed.get('interpretation_confidence')}")
    print(f"Possible Clinical Associations: {parsed.get('possible_clinical_associations')}")
    print("\n")

    # Validate the parsed response
    assert parsed['summary'] == "The ECG shows patterns that may indicate myocardial infarction, which requires clinical correlation."
    assert parsed['primary_finding'] == "ECG patterns suggestive of myocardial infarction (heart attack)"
    assert parsed['interpretation_confidence'] == "Moderate"
    assert len(parsed['possible_clinical_associations']) == 3
    assert "May be associated with coronary artery disease" in parsed['possible_clinical_associations']

    print("[OK] Text format parsed successfully")
    print("[OK] All required fields extracted correctly")
    print("[OK] Interpretation confidence validated")

except Exception as e:
    print(f"[FAIL] Error: {e}")
    import traceback
    traceback.print_exc()

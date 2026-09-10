import sys
import os
import json
import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def test_signal():
    t = np.linspace(0, 10, 1000)
    signal = np.zeros((12, 1000), dtype=np.float32)
    for i in range(12):
        signal[i] = 0.1 * np.sin(2 * np.pi * 1.2 * t) + 0.02 * np.random.randn(1000)
    return signal


def test_model_loads():
    from app.ml.model import model_loader
    model = model_loader.get_model()
    assert model is not None
    config = model_loader.get_config()
    assert config["classes"] == ["NORM", "MI", "STTC", "CD", "HYP"]


def test_preprocessing_shape(test_signal):
    from app.ml.preprocessing import preprocess_signal, validate_signal
    is_valid, msg = validate_signal(test_signal)
    assert is_valid
    processed = preprocess_signal(test_signal)
    assert processed.shape == (12, 1000)


def test_predictor_output(test_signal):
    from app.ml.predictor import predictor
    result = predictor.predict(test_signal)
    assert "prediction" in result
    assert "confidence" in result
    assert 0 <= result["confidence"] <= 1
    assert "probabilities" in result
    assert len(result["probabilities"]) == 5
    assert "model_version" in result


def test_validate_invalid_shape():
    from app.ml.preprocessing import validate_signal
    bad = np.zeros((3, 100), dtype=np.float32)
    is_valid, _ = validate_signal(bad)
    assert not is_valid


def test_validate_nan():
    from app.ml.preprocessing import validate_signal
    bad = np.random.randn(12, 1000).astype(np.float32)
    bad[0, 0] = np.nan
    is_valid, _ = validate_signal(bad)
    assert not is_valid


def test_signal_quality():
    from app.services.ecg_service import compute_signal_quality
    clean = np.random.randn(12, 1000).astype(np.float32)
    assert compute_signal_quality(clean) in ["excellent", "good", "fair", "poor"]


def _make_test_image(size=64):
    from PIL import Image
    t = np.linspace(0, 10 * np.pi, size)
    arr = (128 + 60 * np.sin(t)).astype(np.uint8)
    img = np.tile(arr, (size, 1))
    return Image.fromarray(img, "L").convert("RGB")


def test_image_model_loads():
    from app.ml.image_model import image_model_loader
    if not image_model_loader.enabled():
        pytest.skip("Image model disabled")
    model = image_model_loader.get_model()
    assert model is not None
    config = image_model_loader.get_config()
    assert config["model_name"] == "EfficientNet-B0"
    assert len(config["classes"]) == 15


def test_image_preprocessing_shape():
    from app.ml.image_predictor import image_predictor
    img = _make_test_image()
    tensor = image_predictor.preprocess(img)
    assert tensor.shape == (1, 3, 224, 224)


def test_image_predictor_output():
    from app.ml.image_predictor import image_predictor
    if not image_predictor.loader.is_loaded():
        pytest.skip("Image model not loaded")
    img = _make_test_image(224)
    result = image_predictor.predict(img)
    assert "prediction" in result
    assert 0 <= result["confidence"] <= 1
    assert len(result["probabilities"]) == 15
    assert result["prediction"] in result["probabilities"]
    assert "model_name" in result
    assert result["model_name"] == "EfficientNet-B0"


def test_image_gradcam_supported():
    from app.ml.image_predictor import image_predictor
    if not image_predictor.loader.is_loaded():
        pytest.skip("Image model not loaded")
    assert image_predictor.is_gradcam_supported() is True


def test_image_validation_rejects_non_image():
    from app.services.image_service import validate_image_file
    with pytest.raises(ValueError):
        validate_image_file(b"not an image", "test.txt")


def test_interpretation_maps_all_15_subclasses():
    from app.ml.image_interpretation import (
        SUBCLASS_LABELS,
        GROUP_DEFINITIONS,
        subclass_group,
        human_label,
    )
    assert len(SUBCLASS_LABELS) == 15
    assert len(GROUP_DEFINITIONS) == 5
    # every subclass belongs to exactly one group
    all_members = [c for members in GROUP_DEFINITIONS.values() for c in members]
    assert sorted(all_members) == sorted(SUBCLASS_LABELS.keys())
    for cls in SUBCLASS_LABELS:
        assert subclass_group(cls) in GROUP_DEFINITIONS
        assert human_label(cls) != cls


def test_interpretation_aggregates_groups_correctly():
    from app.ml.image_interpretation import (
        compute_group_probabilities,
        verify_distribution,
        interpret_image,
        GROUP_DEFINITIONS,
    )
    import numpy as np
    rng = np.random.default_rng(42)
    probs = rng.dirichlet(np.ones(15))
    labels = list(GROUP_DEFINITIONS["Normal"]) + list(GROUP_DEFINITIONS["Supraventricular"]) \
        + list(GROUP_DEFINITIONS["Ventricular"]) + list(GROUP_DEFINITIONS["Fusion"]) \
        + list(GROUP_DEFINITIONS["Other/Unclassifiable"])
    prob_dict = dict(zip(labels, probs.tolist()))

    groups = compute_group_probabilities(prob_dict)
    assert abs(sum(groups.values()) - 1.0) < 1e-4
    for group, members in GROUP_DEFINITIONS.items():
        assert abs(groups[group] - sum(prob_dict[c] for c in members)) < 1e-6

    verified = verify_distribution(prob_dict)
    assert verified["is_normalized"] is True

    pred_class = labels[int(np.argmax(probs))]
    result = interpret_image(prob_dict, pred_class, float(probs.max()))
    assert result["distribution_verified"] is True
    assert result["primary_prediction"] == pred_class
    assert result["primary_label"] != pred_class
    assert result["dominant_group"] == max(
        groups, key=lambda g: groups[g]
    )
    assert len(result["subclass_results"]) == 15
    assert result["subclass_results"][0]["probability"] == result["primary_confidence"]
    assert result["pattern_summary"]
    assert result["dominant_group"] in result["pattern_summary"]
    assert result["recommended_next_steps"]
    assert "not a disease or risk" in result["medical_disclaimer"] or "not calibrated" in result["medical_disclaimer"]

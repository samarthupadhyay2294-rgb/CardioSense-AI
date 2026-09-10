import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "model_loaded" in data


def test_model_info(client):
    res = client.get("/api/model/info")
    assert res.status_code == 200
    data = res.json()
    assert data["model_name"] == "ECGCNN"
    assert data["input_shape"] == [12, 1000]
    assert len(data["classes"]) == 5


def test_model_status(client):
    res = client.get("/api/model/status")
    assert res.status_code == 200
    data = res.json()
    assert "signal_model" in data
    assert "image_model" in data
    assert "loaded" in data["signal_model"]
    assert "loaded" in data["image_model"]
    assert data["signal_model"]["loaded"] is True


def test_statistics_empty(client):
    res = client.get("/api/statistics")
    assert res.status_code == 200
    data = res.json()
    assert data["total_analyses"] >= 0


def test_history_empty(client):
    res = client.get("/api/ecg/history")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "total" in data


def test_upload_invalid_file(client):
    res = client.post(
        "/api/ecg/analyze",
        files={"files": ("test.txt", b"not an ecg", "text/plain")},
    )
    assert res.status_code in [400, 500]


def test_upload_empty_file(client):
    res = client.post(
        "/api/ecg/analyze",
        files={"files": ("empty.csv", b"", "text/csv")},
    )
    assert res.status_code in [400, 500]


def test_root(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "CardioSense" in res.json()["name"]


def test_docs(client):
    res = client.get("/docs")
    assert res.status_code == 200


def _make_test_image_bytes(size=120):
    import io
    import numpy as np
    from PIL import Image
    t = np.linspace(0, 10 * np.pi, size)
    arr = (128 + 60 * np.sin(t)).astype(np.uint8)
    img = np.tile(arr, (size, 1))
    pil = Image.fromarray(img, "L").convert("RGB")
    buf = io.BytesIO()
    pil.save(buf, format="PNG")
    return buf.getvalue()


def test_image_analyze(client):
    img_bytes = _make_test_image_bytes()
    res = client.post(
        "/api/ecg-image/analyze",
        files={"file": ("ecg.png", img_bytes, "image/png")},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "analysis_id" in data
    assert len(data["probabilities"]) == 15
    assert data["prediction"] == data["primary_label"]  # prediction is the human-readable label
    assert data["primary_prediction"]  # raw class code
    assert data["primary_label"]
    assert data["dominant_group"] in {
        "Normal", "Supraventricular", "Ventricular", "Fusion", "Other/Unclassifiable",
    }
    assert len(data["subclass_results"]) == 15
    assert len(data["group_probabilities"]) == 5
    assert data["pattern_summary"]
    assert data["recommended_next_steps"]
    assert data["next_steps"]
    assert data["medical_disclaimer"]
    assert data["distribution_verified"] is True


def test_image_subclass_results_structure(client):
    import numpy as np
    img_bytes = _make_test_image_bytes()
    res = client.post(
        "/api/ecg-image/analyze",
        files={"file": ("ecg.png", img_bytes, "image/png")},
    )
    data = res.json()
    results = data["subclass_results"]
    # one row per class, all fields present
    assert {r["raw_class"] for r in results} == set(data["probabilities"].keys())
    for r in results:
        assert r["human_readable_label"]
        assert 0.0 <= r["probability"] <= 1.0
        assert r["group"] in data["group_probabilities"]
        assert abs(r["group_probability"] - data["group_probabilities"][r["group"]]) < 1e-6
    # sorted highest -> lowest
    probs = [r["probability"] for r in results]
    assert probs == sorted(probs, reverse=True)
    # subclass probabilities sum to 1.0 (single normalized distribution)
    assert abs(sum(r["probability"] for r in results) - 1.0) < 1e-2
    # group probabilities aggregate the members
    members = {
        "Normal": {"N", "L", "R", "e", "j"},
        "Supraventricular": {"A", "J", "S", "aa"},
        "Ventricular": {"V", "E"},
        "Fusion": {"F"},
        "Other/Unclassifiable": {"Q", "p", "f"},
    }
    for group, classes in members.items():
        expected = sum(data["probabilities"][c] for c in classes)
        assert abs(data["group_probabilities"][group] - expected) < 1e-6


def test_image_get_analysis(client):
    import numpy as np
    img_bytes = _make_test_image_bytes()
    res = client.post(
        "/api/ecg-image/analyze",
        files={"file": ("ecg.png", img_bytes, "image/png")},
    )
    aid = res.json()["analysis_id"]
    res2 = client.get(f"/api/ecg-image/{aid}")
    assert res2.status_code == 200
    a = res2.json()
    assert a["analysis_type"] == "image"
    assert a["prediction"]
    assert a["primary_label"]
    assert a["dominant_group"]
    assert len(a["subclass_results"]) == 15
    assert a["group_probabilities"]
    assert a["pattern_summary"]
    assert a["recommended_next_steps"]
    assert a["medical_disclaimer"]


def test_image_invalid_file(client):
    res = client.post(
        "/api/ecg-image/analyze",
        files={"file": ("test.txt", b"not an image", "text/plain")},
    )
    assert res.status_code == 400


def test_image_model_status(client):
    res = client.get("/api/model/status")
    assert res.status_code == 200
    data = res.json()
    assert "image_model" in data
    assert data["image_model"]["loaded"] is True


def test_image_model_info(client):
    res = client.get("/api/model/image-info")
    assert res.status_code == 200
    data = res.json()
    assert data["model_name"] == "EfficientNet-B0"
    assert len(data["classes"]) == 15


def test_image_gradcam_endpoint(client):
    import numpy as np
    img_bytes = _make_test_image_bytes()
    res = client.post(
        "/api/ecg-image/analyze",
        files={"file": ("ecg.png", img_bytes, "image/png")},
    )
    aid = res.json()["analysis_id"]
    res2 = client.get(f"/api/ecg-image/{aid}/gradcam")
    assert res2.status_code == 200
    assert res2.headers["content-type"].startswith("image")


def test_image_model_unavailable_degrades(client, monkeypatch):
    """When the image model fails to load, the signal pipeline is unaffected."""
    from app.ml.image_model import image_model_loader

    monkeypatch.setattr(image_model_loader, "_model", None)
    monkeypatch.setattr(image_model_loader, "_load_error", "simulated image model failure")
    monkeypatch.setattr(
        image_model_loader, "_config", image_model_loader.get_config(),
    )

    # Health still reports the signal model up, image model down
    health = client.get("/api/health").json()
    assert health["model_loaded"] is True
    assert health["image_model_loaded"] is False

    # Status reflects both
    status = client.get("/api/model/status").json()
    assert status["signal_model"]["loaded"] is True
    assert status["image_model"]["loaded"] is False

    # Signal upload still works
    signal = _make_signal_upload()
    res = client.post("/api/ecg/analyze", files=signal)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["prediction"]["confidence"] > 0


def test_image_analyze_errors_when_model_unavailable(client, monkeypatch):
    from app.ml.image_model import image_model_loader

    monkeypatch.setattr(image_model_loader, "_model", None)
    monkeypatch.setattr(image_model_loader, "_load_error", "simulated image model failure")

    img_bytes = _make_test_image_bytes()
    res = client.post(
        "/api/ecg-image/analyze",
        files={"file": ("ecg.png", img_bytes, "image/png")},
    )
    assert res.status_code == 500
    assert "image" in res.json()["detail"].lower()


def test_image_gradcam_failure_keeps_prediction(client, monkeypatch):
    """A Grad-CAM failure must not fail the prediction — gradcam_available is false."""
    from app.ml.image_predictor import image_predictor

    def _boom(*args, **kwargs):
        raise RuntimeError("simulated gradcam failure")

    monkeypatch.setattr(image_predictor, "generate_gradcam", _boom)

    img_bytes = _make_test_image_bytes()
    res = client.post(
        "/api/ecg-image/analyze",
        files={"file": ("ecg.png", img_bytes, "image/png")},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["gradcam_available"] is False
    assert data["prediction"]


def _make_signal_upload():
    """A minimal valid 12-lead signal (synthetic) for the signal pipeline."""
    import io
    import numpy as np
    t = np.linspace(0, 10, 1000)
    signal = np.zeros((12, 1000), dtype=np.float64)
    for i in range(12):
        signal[i] = 0.1 * np.sin(2 * np.pi * 1.2 * t) + 0.02 * np.random.default_rng(i).standard_normal(1000)
    buf = io.BytesIO()
    np.save(buf, signal)
    return {"files": ("synthetic.npy", buf.getvalue(), "application/octet-stream")}

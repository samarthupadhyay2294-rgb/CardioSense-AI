import os
import time
import uuid
from pathlib import Path
from typing import Dict, Any, Optional

from PIL import Image, UnidentifiedImageError

from app.core.config import settings
from app.ml.image_predictor import image_predictor
from app.ml.image_interpretation import interpret_image

ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
ALLOWED_IMAGE_MIME = {"image/png", "image/jpeg"}
MAX_IMAGE_SIZE = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

IMAGE_UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads" / "ecg_images"
GRADCAM_DIR = Path(__file__).parent.parent.parent / "uploads" / "ecg_gradcams"


def validate_image_file(content: bytes, filename: str, content_type: str = "") -> str:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {ext or 'unknown'}. Expected PNG, JPG, or JPEG."
        )

    if len(content) == 0:
        raise ValueError("Image file is empty.")
    if len(content) > MAX_IMAGE_SIZE:
        raise ValueError(
            f"Image exceeds the maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB} MB."
        )

    if content_type and content_type not in ALLOWED_IMAGE_MIME:
        raise ValueError(f"Unsupported image MIME type: {content_type}")

    try:
        img = Image.open(__import__("io").BytesIO(content))
        img.verify()
        reopened = Image.open(__import__("io").BytesIO(content))
        reopened.convert("RGB")
    except UnidentifiedImageError:
        raise ValueError("File is not a readable image.")
    except Exception as e:
        raise ValueError(f"Corrupted or unreadable image: {e}")

    return ext


def save_image_file(content: bytes, original_filename: str) -> str:
    IMAGE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    ext = Path(original_filename).suffix.lower() or ".png"
    unique_name = f"{uuid.uuid4().hex}{ext}"
    path = IMAGE_UPLOAD_DIR / unique_name
    with open(path, "wb") as f:
        f.write(content)
    return str(path)


def save_gradcam_image(overlay, original_filename: str) -> str:
    from PIL import Image as PILImage

    GRADCAM_DIR.mkdir(parents=True, exist_ok=True)
    ext = Path(original_filename).suffix.lower() or ".png"
    unique_name = f"gradcam_{uuid.uuid4().hex}{ext}"
    path = GRADCAM_DIR / unique_name
    PILImage.fromarray(overlay).save(path)
    return str(path)


def analyze_image(content: bytes, filename: str, content_type: str = "") -> Dict[str, Any]:
    ext = validate_image_file(content, filename, content_type)

    image = Image.open(__import__("io").BytesIO(content)).convert("RGB")

    total_start = time.perf_counter()
    prediction = image_predictor.predict(image)
    prediction["preprocessing_time"] = 0.0
    prediction["total_processing_time"] = round(time.perf_counter() - total_start, 4)

    gradcam_path = None
    gradcam_available = image_predictor.is_gradcam_supported()
    if gradcam_available:
        try:
            overlay, pred_class, confidence = image_predictor.generate_gradcam(image)
            gradcam_path = save_gradcam_image(overlay, filename)
        except Exception:
            gradcam_path = None
            gradcam_available = False

    stored_path = save_image_file(content, filename)

    interpretation = interpret_image(
        probabilities=prediction["probabilities"],
        prediction=prediction["prediction"],
        confidence=prediction["confidence"],
    )

    return {
        "file_name": filename,
        "file_path": stored_path,
        "analysis_type": "image",
        "prediction": interpretation["primary_label"],
        "raw_class": interpretation["raw_class"],
        "human_readable_label": interpretation["human_readable_label"],
        "primary_prediction": interpretation["primary_prediction"],
        "primary_label": interpretation["primary_label"],
        "primary_confidence": interpretation["primary_confidence"],
        "confidence": prediction["confidence"],
        "probabilities": prediction["probabilities"],
        "processing_time": prediction["processing_time"],
        "gradcam_available": gradcam_available,
        "image_path": stored_path,
        "gradcam_path": gradcam_path,
        "warning": prediction.get("warning"),
        "num_classes": len(prediction["probabilities"]),
        "distribution_verified": interpretation["distribution_verified"],
        "distribution_total": interpretation["distribution_total"],
        "dominant_group": interpretation["dominant_group"],
        "group_probabilities": interpretation["group_probabilities"],
        "subclass_results": interpretation["subclass_results"],
        "pattern_summary": interpretation["pattern_summary"],
        "recommended_next_steps": interpretation["recommended_next_steps"],
        "next_steps": interpretation["recommended_next_steps"],
        "medical_disclaimer": interpretation["medical_disclaimer"],
    }

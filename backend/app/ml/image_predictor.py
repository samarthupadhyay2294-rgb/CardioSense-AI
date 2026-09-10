import json
import time
from typing import Dict, Any, Optional, Tuple

import numpy as np
import torch
from PIL import Image, UnidentifiedImageError

import torchvision.transforms as T

from app.core.config import settings
from app.ml.image_model import image_model_loader

CONFIDENCE_THRESHOLD = 0.60


class ECGImagePredictor:
    def __init__(self, loader=None):
        self.loader = loader or image_model_loader

    def config(self) -> Dict[str, Any]:
        return self.loader.get_config()

    def model_name(self) -> str:
        return self.config().get("model_name", "EfficientNet-B0")

    def model_version(self) -> str:
        return self.config().get("model_version", "1.0")

    def classes(self) -> list:
        return self.config().get("classes", [])

    def idx_to_class(self) -> Dict[int, str]:
        mapping = self.config().get("class_mapping", {})
        return {v: k for k, v in mapping.items()}

    def input_size(self) -> Tuple[int, int]:
        size = self.config().get("input_size", [224, 224])
        return size[0], size[1]

    def _build_transforms(self) -> T.Compose:
        size = self.input_size()
        mean = self.config().get("normalization", {}).get("mean", [0.485, 0.456, 0.406])
        std = self.config().get("normalization", {}).get("std", [0.229, 0.224, 0.225])
        return T.Compose([
            T.Resize((size[0] + 20, size[1] + 20)),
            T.CenterCrop(size),
            T.ToTensor(),
            T.Normalize(mean=mean, std=std),
        ])

    def preprocess(self, image: Image.Image) -> torch.Tensor:
        tfm = self._build_transforms()
        return tfm(image.convert("RGB")).unsqueeze(0)

    def predict(self, image: Image.Image) -> Dict[str, Any]:
        model = self.loader.get_model()
        if model is None:
            raise RuntimeError(
                "Image model is unavailable. ECG image analysis cannot run at this time."
            )

        device = self.loader.get_device()
        tensor = self.preprocess(image).to(device)

        start = time.perf_counter()
        with torch.inference_mode():
            outputs = model(tensor)
            probs = torch.softmax(outputs, dim=1).squeeze().cpu().numpy()
        inference_time = time.perf_counter() - start

        pred_idx = int(np.argmax(probs))
        confidence = float(probs[pred_idx])
        idx_to_class = self.idx_to_class()

        result = {
            "prediction": idx_to_class[pred_idx],
            "confidence": confidence,
            "probabilities": {idx_to_class[i]: float(p) for i, p in enumerate(probs)},
            "model_name": self.model_name(),
            "model_version": self.model_version(),
            "prediction_code": idx_to_class[pred_idx],
            "processing_time": inference_time,
        }
        if confidence < CONFIDENCE_THRESHOLD:
            result["warning"] = (
                "Low model confidence. The ECG image may be difficult to classify reliably."
            )
        return result

    def is_gradcam_supported(self) -> bool:
        try:
            model = self.loader.get_model()
            return model is not None and hasattr(model, "features") and len(model.features) > 0
        except Exception:
            return False

    def generate_gradcam(self, image: Image.Image) -> Tuple[np.ndarray, str, float]:
        from app.ml.image_gradcam import GradCAM, overlay_heatmap

        model = self.loader.get_model()
        if model is None:
            raise RuntimeError("Image model is unavailable.")
        device = self.loader.get_device()

        cam_engine = GradCAM(model)
        try:
            tensor = self.preprocess(image).to(device)
            cam, pred_idx, probs = cam_engine.generate(tensor)
            overlay = overlay_heatmap(image.convert("RGB"), cam)
            idx_to_class = self.idx_to_class()
            return overlay, idx_to_class[pred_idx], float(probs[pred_idx])
        finally:
            cam_engine.remove_hooks()


image_predictor = ECGImagePredictor()
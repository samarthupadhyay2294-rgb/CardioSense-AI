import json
import torch
import torch.nn as nn
from pathlib import Path
from typing import Dict, Any

from app.core.config import settings


def create_efficientnet_b0(num_classes: int):
    from torchvision.models import efficientnet_b0
    model = efficientnet_b0(weights=None)
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, num_classes)
    return model


class ImageModelLoader:
    _instance = None
    _model = None
    _config = None
    _device = None
    _load_error = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def enabled(self) -> bool:
        return bool(getattr(settings, "ENABLE_IMAGE_MODEL", True))

    def get_device(self) -> torch.device:
        if self._device is None:
            self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        return self._device

    def load_config(self) -> Dict[str, Any]:
        if self._config is None:
            with open(settings.IMAGE_MODEL_CONFIG, "r") as f:
                self._config = json.load(f)
        return self._config

    def load_model(self):
        if not self.enabled():
            self._load_error = "Image model disabled via ENABLE_IMAGE_MODEL"
            return None
        if self._model is not None:
            return self._model

        config = self.load_config()
        device = self.get_device()
        class_mapping = config["class_mapping"]
        model = create_efficientnet_b0(num_classes=len(class_mapping))
        checkpoint = torch.load(settings.IMAGE_MODEL_PATH, map_location=device)
        model.load_state_dict(checkpoint["model_state_dict"])
        model.to(device)
        model.eval()
        self._model = model
        return self._model

    def get_model(self):
        if self._model is None and self._load_error is None:
            try:
                return self.load_model()
            except Exception as e:
                self._load_error = str(e)
                return None
        return self._model

    def get_config(self) -> Dict[str, Any]:
        if self._config is None:
            return self.load_config()
        return self._config

    def is_loaded(self) -> bool:
        return self._model is not None

    def clear_error(self):
        self._load_error = None


image_model_loader = ImageModelLoader()
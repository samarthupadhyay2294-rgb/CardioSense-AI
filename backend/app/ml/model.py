import torch
import torch.nn as nn
from typing import Dict, Any
import json
from pathlib import Path

from app.core.config import settings


class ECGCNN(nn.Module):
    def __init__(self, in_channels: int = 12, n_classes: int = 5, dropout: float = 0.4):
        super().__init__()
        self.block1 = self._conv_block(in_channels, 32)
        self.block2 = self._conv_block(32, 64)
        self.block3 = self._conv_block(64, 128)
        self.block4 = self._conv_block(128, 256)
        self.gap = nn.AdaptiveAvgPool1d(1)
        self.fc = nn.Sequential(
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, n_classes)
        )

    def _conv_block(self, in_c: int, out_c: int) -> nn.Sequential:
        return nn.Sequential(
            nn.Conv1d(in_c, out_c, kernel_size=7, padding=3),
            nn.BatchNorm1d(out_c),
            nn.ReLU(),
            nn.MaxPool1d(2)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.block1(x)
        x = self.block2(x)
        x = self.block3(x)
        x = self.block4(x)
        x = self.gap(x).squeeze(-1)
        return self.fc(x)


class ModelLoader:
    _instance = None
    _model = None
    _config = None
    _device = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_config(self) -> Dict[str, Any]:
        if self._config is None:
            with open(settings.MODEL_CONFIG_PATH, "r") as f:
                self._config = json.load(f)
        return self._config

    def get_device(self) -> torch.device:
        if self._device is None:
            self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        return self._device

    def load_model(self) -> ECGCNN:
        if self._model is not None:
            return self._model

        config = self.load_config()
        device = self.get_device()

        model_params = config["model_parameters"]
        self._model = ECGCNN(
            in_channels=model_params["in_channels"],
            n_classes=model_params["n_classes"],
            dropout=model_params["dropout"]
        ).to(device)

        state_dict = torch.load(settings.MODEL_PATH, map_location=device)
        self._model.load_state_dict(state_dict)
        self._model.eval()

        return self._model

    def get_model(self) -> ECGCNN:
        if self._model is None:
            return self.load_model()
        return self._model

    def get_config(self) -> Dict[str, Any]:
        if self._config is None:
            return self.load_config()
        return self._config


model_loader = ModelLoader()
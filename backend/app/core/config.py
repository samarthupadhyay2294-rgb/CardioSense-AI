import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    MODEL_PATH: str = str(Path(__file__).parent.parent.parent / "models" / "ptbxl_cnn_best.pt")
    MODEL_CONFIG_PATH: str = str(Path(__file__).parent.parent.parent / "config" / "model_config.json")
    SIGNAL_MODEL_PATH: str = MODEL_PATH
    IMAGE_MODEL_PATH: str = str(Path(__file__).parent.parent.parent / "models" / "image" / "best_model.pt")
    IMAGE_MODEL_CONFIG: str = str(Path(__file__).parent.parent.parent / "models" / "image" / "model_config.json")
    IMAGE_MODEL_NAME: str = "ECG Image Classifier"
    IMAGE_MODEL_VERSION: str = "1.0"
    ENABLE_IMAGE_MODEL: bool = True
    DATABASE_URL: str = "sqlite:///./cardiosense.db"
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]
    MAX_UPLOAD_SIZE_MB: int = 20
    MODEL_VERSION: str = "1.0"
    ENVIRONMENT: str = "development"


settings = Settings()
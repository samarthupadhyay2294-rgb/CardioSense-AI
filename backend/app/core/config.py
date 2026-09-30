import json
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import Any, List, Optional, Union


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    MODEL_PATH: str = str(Path(__file__).parent.parent.parent / "models" / "ptbxl_cnn_best.pt")
    MODEL_CONFIG_PATH: str = str(Path(__file__).parent.parent.parent / "config" / "model_config.json")
    SIGNAL_MODEL_PATH: str = MODEL_PATH
    IMAGE_MODEL_PATH: str = str(Path(__file__).parent.parent.parent / "models" / "image" / "best_model.pt")
    IMAGE_MODEL_CONFIG: str = str(Path(__file__).parent.parent.parent / "models" / "image" / "model_config.json")
    IMAGE_MODEL_NAME: str = "ECG Image Classifier"
    IMAGE_MODEL_VERSION: str = "1.0"
    ENABLE_IMAGE_MODEL: bool = True
    DATABASE_URL: str = "sqlite:///./cardiosense.db"
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    MAX_UPLOAD_SIZE_MB: int = 20
    MODEL_VERSION: str = "1.0"
    ENVIRONMENT: str = "development"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-flash"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> Any:
        if isinstance(v, str):
            v_str = v.strip()
            if v_str.startswith("[") and v_str.endswith("]"):
                try:
                    return json.loads(v_str)
                except Exception:
                    pass
            return [x.strip() for x in v_str.split(",") if x.strip()]
        return v


settings = Settings()
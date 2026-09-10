from fastapi import APIRouter
from app.core.config import settings
from app.ml.model import model_loader
from app.ml.image_model import image_model_loader
from app.database.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/api/health", response_model=HealthResponse)
def health_check():
    try:
        model = model_loader.get_model()
        model_loaded = model is not None
        device = str(model_loader.get_device())
    except Exception:
        model_loaded = False
        device = "unavailable"

    try:
        image_loaded = image_model_loader.is_loaded()
    except Exception:
        image_loaded = False

    return HealthResponse(
        status="ok",
        model_loaded=model_loaded,
        device=device,
        version=settings.MODEL_VERSION,
        image_model_loaded=image_loaded
    )
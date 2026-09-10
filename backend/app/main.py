from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.database.database import init_db
from app.ml.model import model_loader
from app.ml.image_model import image_model_loader

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    try:
        model_loader.get_model()
        logger.info("Model loaded successfully at startup")
    except Exception as e:
        logger.error(f"Failed to load model at startup: {e}")
    # Image model is isolated: a failure here must NOT affect signal analysis
    try:
        image_model_loader.get_model()
        logger.info("Image model loaded successfully at startup")
    except Exception as e:
        image_model_loader._load_error = str(e)
        logger.error(f"Failed to load image model at startup: {e}")
    yield
    logger.info("Shutting down")


app = FastAPI(
    title="CardioSense AI",
    description="Intelligent ECG Analysis. Clearer Cardiac Insights.\n\n"
                "AI-powered ECG signal analysis API. Upload ECG recordings and receive "
                "predictions from a trained deep learning model.",
    version=settings.MODEL_VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.health import router as health_router
from app.api.ecg import router as ecg_router
from app.api.history import router as history_router
from app.api.statistics import router as statistics_router
from app.api.model import router as model_router
from app.api.image_ecg import router as image_ecg_router

app.include_router(health_router)
app.include_router(history_router)
app.include_router(ecg_router)
app.include_router(statistics_router)
app.include_router(model_router)
app.include_router(image_ecg_router)


@app.get("/")
def root():
    return {
        "name": "CardioSense AI API",
        "version": settings.MODEL_VERSION,
        "docs": "/docs",
        "health": "/api/health"
    }
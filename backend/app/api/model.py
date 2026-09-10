from fastapi import APIRouter
from app.ml.model import model_loader
from app.ml.image_model import image_model_loader
from app.database.schemas import ModelInfoResponse
from app.core.config import settings

router = APIRouter(tags=["model"])


@router.get("/api/model/info", response_model=ModelInfoResponse)
def model_info():
    config = model_loader.get_config()
    device = str(model_loader.get_device())

    test_metrics = config.get("test_metrics") or {
        "NORM AUC": 0.9413,
        "MI AUC": 0.9252,
        "STTC AUC": 0.9350,
        "CD AUC": 0.9230,
        "HYP AUC": 0.8395,
        "Mean Test AUC": 0.9128
    }

    return ModelInfoResponse(
        model_name=config.get("model_name", "ECGCNN"),
        model_version=config.get("model_version", settings.MODEL_VERSION),
        architecture="1D Convolutional Neural Network (ECGCNN)",
        input_shape=config.get("input_shape", [12, 1000]),
        sampling_rate=config.get("sampling_rate", 100),
        num_leads=config.get("num_leads", 12),
        signal_length=config.get("time_points", 1000),
        classes=config.get("classes", []),
        class_names=config.get("class_names", {}),
        class_descriptions=config.get("class_descriptions", {}),
        preprocessing=config.get("preprocessing", {}),
        model_parameters=config.get("model_parameters", {}),
        thresholds=config.get("thresholds", {}),
        training_config=config.get("training_config", {}),
        test_metrics=test_metrics
    )


@router.get("/api/model/image-info")
def image_model_info():
    config = image_model_loader.get_config()
    return {
        "model_name": config.get("model_name"),
        "model_version": config.get("model_version"),
        "architecture": "EfficientNet-B0",
        "input_size": config.get("input_size"),
        "classes": config.get("classes"),
        "class_mapping": config.get("class_mapping"),
        "normalization": config.get("normalization"),
        "gradcam_supported": image_model_loader.is_loaded(),
        "framework": "PyTorch + torchvision",
        "loaded": image_model_loader.is_loaded(),
    }


@router.get("/api/model/status")
def model_status():
    config = model_loader.get_config()
    device = str(model_loader.get_device())

    try:
        model = model_loader.get_model()
        signal_loaded = model is not None
    except Exception:
        signal_loaded = False

    try:
        image_model_loader.get_model()
        image_loaded = image_model_loader.is_loaded()
    except Exception:
        image_loaded = False

    return {
        "signal_model": {
            "loaded": signal_loaded,
            "model_name": config.get("model_name"),
            "model_version": config.get("model_version", settings.MODEL_VERSION),
            "num_classes": len(config.get("classes", [])),
            "input_shape": config.get("input_shape"),
            "thresholds": config.get("thresholds", {}),
            "device": device,
        },
        "image_model": {
            "loaded": image_loaded,
            "model_name": image_model_loader.get_config().get("model_name"),
            "model_version": image_model_loader.get_config().get("model_version"),
            "num_classes": len(image_model_loader.get_config().get("classes", [])),
            "input_size": image_model_loader.get_config().get("input_size"),
            "device": device,
        },
    }
"""
Gemini Interpretation Router for CardioSense AI
Exposes POST /api/interpretation/gemini endpoint.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import ECGAnalysis
from app.ml.prediction_normalizer import prediction_normalizer
from app.services.gemini_service import (
    gemini_interpretation_service,
    GeminiConfigurationError,
    GeminiAPIError
)

router = APIRouter(tags=["interpretation"])


class GeminiInterpretationRequest(BaseModel):
    analysis_id: Optional[int] = None
    prediction: Optional[Dict[str, Any]] = None


@router.post("/api/interpretation/gemini")
def get_gemini_interpretation(
    request: GeminiInterpretationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate LLM clinical interpretation via Gemini for a given analysis_id or raw prediction dict.
    """
    if not gemini_interpretation_service.is_available():
        try:
            gemini_interpretation_service.initialize()
        except Exception:
            pass

    if not gemini_interpretation_service.is_available():
        raise HTTPException(
            status_code=503,
            detail={
                "code": "GEMINI_NOT_CONFIGURED",
                "message": "Gemini API service is not configured or unavailable"
            }
        )

    if request.analysis_id is not None:
        analysis = db.query(ECGAnalysis).filter(ECGAnalysis.id == request.analysis_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        normalized = prediction_normalizer.normalize_from_analysis_dict(analysis.to_dict())
    elif request.prediction is not None:
        if "prediction" not in request.prediction:
            raise HTTPException(status_code=400, detail="Invalid prediction dictionary")
        if request.prediction.get("analysis_type") == "image":
            normalized = prediction_normalizer.normalize_image_prediction(request.prediction)
        else:
            normalized = prediction_normalizer.normalize_signal_prediction(request.prediction)
    else:
        raise HTTPException(status_code=400, detail="Must provide analysis_id or prediction")

    try:
        interpretation = gemini_interpretation_service.interpret_prediction(normalized)
        return {
            "success": True,
            "interpretation": interpretation
        }
    except GeminiConfigurationError as e:
        raise HTTPException(status_code=500, detail={"code": "GEMINI_CONFIGURATION_ERROR", "message": str(e)})
    except GeminiAPIError as e:
        raise HTTPException(status_code=502, detail={"code": "GEMINI_API_ERROR", "message": str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"code": "INTERNAL_ERROR", "message": str(e)})

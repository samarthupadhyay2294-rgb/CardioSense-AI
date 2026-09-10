from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Depends, Query, Form, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

from app.core.config import settings
from app.database.database import get_db
from app.database.models import ECGAnalysis
from app.database.schemas import ImageAnalysisResponse, ECGAnalysisResponse
from app.services.image_service import analyze_image, IMAGE_UPLOAD_DIR, GRADCAM_DIR

router = APIRouter(tags=["ecg-image"])


@router.post("/api/ecg-image/analyze", response_model=ImageAnalysisResponse)
async def analyze_ecg_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    filename = file.filename or "upload.png"
    content = await file.read()
    content_type = file.content_type or ""

    try:
        result = analyze_image(content, filename, content_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")

    analysis = ECGAnalysis(
        analysis_type="image",
        file_name=result["file_name"],
        file_path=result["image_path"],
        prediction=result["prediction"],
        prediction_code=result["raw_class"],
        confidence=result["confidence"],
        probabilities=result["probabilities"],
        model_name=result.get("model_name") or settings.IMAGE_MODEL_NAME,
        model_version=result.get("model_version") or "1.0",
        processing_time=result["processing_time"],
        image_path=result["image_path"],
        gradcam_path=result["gradcam_path"],
        gradcam_available=1 if result["gradcam_available"] else 0,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return ImageAnalysisResponse(
        success=True,
        message="ECG image analyzed successfully",
        analysis_id=analysis.id,
        analysis_type="image",
        file_name=analysis.file_name,
        prediction=result["primary_label"],
        confidence=result["confidence"],
        probabilities=result["probabilities"],
        processing_time=analysis.processing_time,
        gradcam_available=bool(analysis.gradcam_available),
        warning=result.get("warning"),
        distribution_verified=result.get("distribution_verified"),
        primary_prediction=result.get("primary_prediction"),
        primary_label=result.get("primary_label"),
        primary_confidence=result.get("primary_confidence"),
        dominant_group=result.get("dominant_group"),
        group_probabilities=result.get("group_probabilities"),
        subclass_results=result.get("subclass_results"),
        pattern_summary=result.get("pattern_summary"),
        recommended_next_steps=result.get("recommended_next_steps"),
        next_steps=result.get("recommended_next_steps"),
        medical_disclaimer=result.get("medical_disclaimer"),
    )


def _enrich_image_response(analysis):
    """Attach the interpretation fields to a stored image analysis.

    The interpretation is deterministic from the saved model probabilities, so it is
    recomputed on read for records that predate this feature (or lack the fields).
    """
    from app.ml.image_interpretation import interpret_image
    if not analysis.probabilities:
        return
    interpretation = interpret_image(
        probabilities=analysis.probabilities,
        prediction=analysis.prediction_code,
        confidence=analysis.confidence,
    )
    analysis.distribution_verified = interpretation["distribution_verified"]
    analysis.distribution_total = interpretation["distribution_total"]
    analysis.primary_prediction = interpretation["primary_prediction"]
    analysis.primary_label = interpretation["primary_label"]
    analysis.primary_confidence = interpretation["primary_confidence"]
    analysis.dominant_group = interpretation["dominant_group"]
    analysis.group_probabilities = interpretation["group_probabilities"]
    analysis.subclass_results = interpretation["subclass_results"]
    analysis.pattern_summary = interpretation["pattern_summary"]
    analysis.recommended_next_steps = interpretation["recommended_next_steps"]
    analysis.next_steps = interpretation["recommended_next_steps"]
    analysis.medical_disclaimer = interpretation["medical_disclaimer"]


@router.get("/api/ecg-image/{analysis_id}", response_model=ECGAnalysisResponse)
def get_image_analysis(analysis_id: int, db: Session = Depends(get_db)):
    analysis = db.query(ECGAnalysis).filter(
        ECGAnalysis.id == analysis_id,
        ECGAnalysis.analysis_type == "image"
    ).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Image analysis not found")
    _enrich_image_response(analysis)
    return analysis


@router.get("/api/ecg-image/{analysis_id}/image")
def get_image_file(analysis_id: int, db: Session = Depends(get_db)):
    analysis = db.query(ECGAnalysis).filter(ECGAnalysis.id == analysis_id).first()
    if not analysis or not analysis.image_path:
        raise HTTPException(status_code=404, detail="Image not found")
    if not Path(analysis.image_path).exists():
        raise HTTPException(status_code=404, detail="Image file is missing")
    return FileResponse(analysis.image_path, media_type="image/png")


@router.get("/api/ecg-image/{analysis_id}/gradcam")
def get_gradcam_file(analysis_id: int, db: Session = Depends(get_db)):
    analysis = db.query(ECGAnalysis).filter(ECGAnalysis.id == analysis_id).first()
    if not analysis or not analysis.gradcam_path:
        raise HTTPException(status_code=404, detail="Grad-CAM not available")
    if not Path(analysis.gradcam_path).exists():
        raise HTTPException(status_code=404, detail="Grad-CAM file is missing")
    return FileResponse(analysis.gradcam_path, media_type="image/png")


@router.get("/api/ecg-image/report/{analysis_id}")
def get_image_report(analysis_id: int, db: Session = Depends(get_db)):
    from app.services.report_service import report_service
    analysis = db.query(ECGAnalysis).filter(ECGAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    try:
        _enrich_image_response(analysis)
        report_path = report_service.generate_report(analysis.to_dict())
        return FileResponse(
            report_path,
            media_type="application/pdf",
            filename=f"cardiosense_image_report_{analysis_id}.pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.post("/api/ecg-image/{analysis_id}/summary")
def get_image_summary(analysis_id: int, db: Session = Depends(get_db)):
    from app.services.summary_service import summary_service
    analysis = db.query(ECGAnalysis).filter(ECGAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    _enrich_image_response(analysis)
    summary = summary_service.generate_summary(analysis.to_dict())
    return {"summary": summary, "analysis_id": analysis_id}


@router.post("/api/ecg-image/{analysis_id}/assistant")
def assistant_query(
    analysis_id: int,
    question: str = Form(...),
    db: Session = Depends(get_db)
):
    from app.services.summary_service import summary_service
    analysis = db.query(ECGAnalysis).filter(ECGAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    _enrich_image_response(analysis)
    answer = summary_service.answer_question(analysis.to_dict(), question)
    return {"answer": answer, "analysis_id": analysis_id}

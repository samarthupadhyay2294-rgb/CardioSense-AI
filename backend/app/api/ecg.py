import os
import shutil
import zipfile
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query, Form
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

from app.core.config import settings
from app.database.database import get_db
from app.database.models import ECGAnalysis
from app.services.ecg_service import (
    process_ecg_file,
    save_uploaded_file,
    read_ecg_file,
    validate_ecg_signal,
    compute_signal_quality,
    compute_ecg_statistics
)
from app.ml.predictor import predictor
from app.database.schemas import ECGAnalysisResponse, ECGUploadResponse, ErrorResponse

router = APIRouter(tags=["ecg"])

ALLOWED_SINGLE_EXTENSIONS = {".mat", ".csv", ".npy", ".txt"}
ALLOWED_WFDB_EXTENSIONS = {".dat", ".hea"}
MAX_SIZE = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"


@router.get("/api/ecg/{analysis_id}", response_model=ECGAnalysisResponse)
def get_ecg_analysis(analysis_id: int, db: Session = Depends(get_db)):
    analysis = db.query(ECGAnalysis).filter(ECGAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis


@router.delete("/api/ecg/{analysis_id}")
def delete_ecg_analysis(analysis_id: int, db: Session = Depends(get_db)):
    analysis = db.query(ECGAnalysis).filter(ECGAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    db.delete(analysis)
    db.commit()
    return {"success": True, "message": "Analysis deleted"}


def _save_wfdb_pair(files: list) -> str:
    base_name = None
    file_map = {}
    
    for file in files:
        filename = file.filename
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_WFDB_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Unsupported file extension: {ext}")
        
        safe = "".join(c for c in filename if c.isalnum() or c in "._-")
        file_map[safe] = file
    
    dat_files = [f for f in file_map if f.endswith(".dat")]
    hea_files = [f for f in file_map if f.endswith(".hea")]
    
    if not dat_files or not hea_files:
        raise HTTPException(status_code=400, detail="WFDB upload requires both .dat and .hea files")
    
    record_dir = UPLOAD_DIR / "wfdb_records"
    record_dir.mkdir(parents=True, exist_ok=True)
    
    for filename, file in file_map.items():
        content = file.file.read()
        if len(content) > MAX_SIZE:
            raise HTTPException(status_code=413, detail="File exceeds maximum upload size")
        dest = record_dir / filename
        with open(dest, "wb") as f:
            f.write(content)
    
    hea_name = hea_files[0]
    return str(record_dir / hea_name)


@router.post("/api/ecg/upload", response_model=ECGUploadResponse)
async def upload_ecg(
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    try:
        if len(files) == 1:
            file = files[0]
            filename = file.filename or "upload"
            ext = Path(filename).suffix.lower()
            
            if ext not in ALLOWED_SINGLE_EXTENSIONS and ext not in ALLOWED_WFDB_EXTENSIONS:
                raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")
            
            content = file.file.read()
            if len(content) == 0:
                raise HTTPException(status_code=400, detail="Empty file uploaded")
            if len(content) > MAX_SIZE:
                raise HTTPException(status_code=413, detail="File exceeds maximum upload size")
            
            file_path = save_uploaded_file(content, filename)
            result = await process_ecg_file(file_path, filename)
        else:
            hea_path = _save_wfdb_pair(files)
            hea_name = Path(hea_path).name
            result = await process_ecg_file(hea_path, hea_name)
        
        analysis = ECGAnalysis(
            file_name=result["file_name"],
            file_path=result.get("file_path"),
            prediction=result["prediction"],
            prediction_code=result["prediction_code"],
            confidence=result["confidence"],
            probabilities=result["probabilities"],
            all_predictions=result["all_predictions"],
            signal_quality=result["signal_quality"],
            sampling_rate=result["sampling_rate"],
            duration=result["duration"],
            num_leads=result["num_leads"],
            model_version=result["model_version"],
            processing_time=result["processing_time"],
            explainability=result.get("explainability"),
            ecg_statistics=result.get("ecg_statistics"),
            signal_data=result.get("signal_data")
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        return ECGUploadResponse(
            success=True,
            message="ECG analyzed successfully",
            analysis_id=analysis.id,
            prediction=result
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/api/ecg/analyze")
async def analyze_ecg(
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    return await upload_ecg(files, db)


@router.get("/api/ecg/report/{analysis_id}")
def get_report(analysis_id: int, db: Session = Depends(get_db)):
    from app.services.report_service import report_service
    
    analysis = db.query(ECGAnalysis).filter(ECGAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    try:
        report_path = report_service.generate_report(analysis.to_dict())
        return FileResponse(
            report_path,
            media_type="application/pdf",
            filename=f"cardiosense_report_{analysis_id}.pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.post("/api/ecg/{analysis_id}/summary")
def get_summary(analysis_id: int, db: Session = Depends(get_db)):
    from app.services.summary_service import summary_service
    from app.ml.model import model_loader
    
    analysis = db.query(ECGAnalysis).filter(ECGAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    config = model_loader.get_config()
    summary_service.set_class_descriptions(config.get("class_descriptions", {}))
    
    summary = summary_service.generate_summary(analysis.to_dict())
    return {"summary": summary, "analysis_id": analysis_id}


@router.post("/api/ecg/{analysis_id}/assistant")
def assistant_query(
    analysis_id: int,
    question: str = Form(...),
    db: Session = Depends(get_db)
):
    from app.services.summary_service import summary_service
    from app.ml.model import model_loader
    
    analysis = db.query(ECGAnalysis).filter(ECGAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    config = model_loader.get_config()
    summary_service.set_class_descriptions(config.get("class_descriptions", {}))
    
    answer = summary_service.answer_question(analysis.to_dict(), question)
    return {"answer": answer, "analysis_id": analysis_id}
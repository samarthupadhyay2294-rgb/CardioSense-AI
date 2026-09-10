from typing import Dict, List, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.database.database import get_db
from app.database.models import ECGAnalysis
from app.database.schemas import StatisticsResponse

router = APIRouter(tags=["statistics"])


@router.get("/api/statistics", response_model=StatisticsResponse)
def get_statistics(db: Session = Depends(get_db)):
    total_analyses = db.query(func.count(ECGAnalysis.id)).scalar() or 0
    
    normal_count = db.query(func.count(ECGAnalysis.id)).filter(
        ECGAnalysis.prediction_code == "NORM"
    ).scalar() or 0
    
    abnormal_count = total_analyses - normal_count
    
    signal_count = db.query(func.count(ECGAnalysis.id)).filter(
        ECGAnalysis.analysis_type == "signal"
    ).scalar() or 0
    
    image_count = db.query(func.count(ECGAnalysis.id)).filter(
        ECGAnalysis.analysis_type == "image"
    ).scalar() or 0
    
    avg_confidence = db.query(func.avg(ECGAnalysis.confidence)).scalar() or 0
    
    prediction_rows = db.query(
        ECGAnalysis.prediction, func.count(ECGAnalysis.id)
    ).filter(ECGAnalysis.analysis_type == "signal").group_by(ECGAnalysis.prediction).all()
    prediction_distribution = {pred: count for pred, count in prediction_rows}
    
    image_prediction_rows = db.query(
        ECGAnalysis.prediction, func.count(ECGAnalysis.id)
    ).filter(ECGAnalysis.analysis_type == "image").group_by(ECGAnalysis.prediction).all()
    image_prediction_distribution = {pred: count for pred, count in image_prediction_rows}
    
    confidence_rows = db.query(
        func.round(ECGAnalysis.confidence * 100, -1),
        func.count(ECGAnalysis.id)
    ).group_by(func.round(ECGAnalysis.confidence * 100, -1)).all()
    confidence_distribution = {f"{int(bucket)}-{int(bucket) + 10}%": count for bucket, count in confidence_rows}
    
    trend_rows = db.query(
        func.strftime("%Y-%m-%d", ECGAnalysis.created_at),
        func.count(ECGAnalysis.id)
    ).group_by(func.strftime("%Y-%m-%d", ECGAnalysis.created_at)).order_by(
        func.strftime("%Y-%m-%d", ECGAnalysis.created_at)
    ).all()
    trend_data = [{"date": date, "count": count} for date, count in trend_rows]
    
    most_common_row = db.query(
        ECGAnalysis.prediction, func.count(ECGAnalysis.id)
    ).group_by(ECGAnalysis.prediction).order_by(func.count(ECGAnalysis.id).desc()).first()
    most_common_prediction = most_common_row[0] if most_common_row else "N/A"
    
    avg_processing = db.query(func.avg(ECGAnalysis.processing_time)).scalar() or 0
    
    return StatisticsResponse(
        total_analyses=total_analyses,
        normal_count=normal_count,
        abnormal_count=abnormal_count,
        signal_count=signal_count,
        image_count=image_count,
        average_confidence=round(float(avg_confidence), 4),
        prediction_distribution=prediction_distribution,
        image_prediction_distribution=image_prediction_distribution,
        confidence_distribution=confidence_distribution,
        trend_data=trend_data,
        most_common_prediction=most_common_prediction,
        average_processing_time=round(float(avg_processing), 4)
    )
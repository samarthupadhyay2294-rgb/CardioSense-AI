from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import ECGAnalysis
from app.database.schemas import PaginatedResponse

router = APIRouter(tags=["history"])


@router.get("/api/ecg/history", response_model=PaginatedResponse)
def get_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    prediction: Optional[str] = Query(None),
    analysis_type: Optional[str] = Query(None, description="Filter by 'signal' or 'image'"),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    db: Session = Depends(get_db)
):
    query = db.query(ECGAnalysis)
    
    if search:
        query = query.filter(ECGAnalysis.file_name.ilike(f"%{search}%"))
    
    if prediction:
        query = query.filter(ECGAnalysis.prediction_code == prediction)
    
    if analysis_type:
        query = query.filter(ECGAnalysis.analysis_type == analysis_type)
    
    total = query.count()
    
    sort_column = getattr(ECGAnalysis, sort_by, ECGAnalysis.created_at)
    if sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
    
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )
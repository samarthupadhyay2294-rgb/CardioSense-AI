"""
Batch ECG Processing API

Provides endpoints for batch ECG analysis, including upload, processing,
and export functionality.
"""

import csv
import io
import json
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import StreamingResponse
from starlette.responses import JSONResponse

from app.services.batch_processing import batch_processor
from app.core.config import settings

router = APIRouter(tags=["batch"])

ALLOWED_EXTENSIONS = {".mat", ".csv", ".npy", ".txt", ".dat", ".hea"}
MAX_SIZE = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
MAX_BATCH_FILES = 50  # Maximum files per batch


@router.post("/api/batch/analyze")
async def analyze_batch(
    files:list[UploadFile] = File(...)
):
    """
    Analyze multiple ECG files in batch.
    
    Accepts multiple ECG files and processes them through the standard pipeline:
    - File validation
    - Signal loading
    - Preprocessing
    - Feature extraction
    - ML prediction
    - Clinical interpretation
    
    Returns batch results with success/failure status for each file.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    if len(files) > MAX_BATCH_FILES:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {MAX_BATCH_FILES} files allowed per batch"
        )
    
    # Validate file extensions
    files_data = []
    for file in files:
        filename = file.filename or "upload"
        ext = Path(filename).suffix.lower()
        
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file extension: {ext}"
            )
        
        # Check file size
        content = file.file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail=f"Empty file: {filename}")
        if len(content) > MAX_SIZE:
            raise HTTPException(status_code=413, detail=f"File exceeds maximum size: {filename}")
        
        files_data.append((content, filename))
    
    # Process batch
    try:
        result = await batch_processor.process_batch(files_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")


@router.get("/api/batch/{batch_id}")
async def get_batch_result(batch_id: str):
    """
    Get batch processing results by batch ID.
    """
    result = batch_processor.get_batch_result(batch_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    return result


@router.get("/api/batch/{batch_id}/export/csv")
async def export_batch_csv(
    batch_id: str,
    status_filter: Optional[str] = Query(None)
):
    """
    Export batch results as CSV.
    
    Includes:
    - file name
    - status
    - prediction
    - confidence
    - interpretation summary
    """
    result = batch_processor.get_batch_result(batch_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    # Apply filter if specified
    results = result['results']
    if status_filter:
        results = [r for r in results if r.get('status') == status_filter]
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'file_name',
        'status',
        'prediction',
        'prediction_code',
        'confidence',
        'signal_quality',
        'clinical_significance',
        'urgency',
        'error'
    ])
    
    # Rows
    for r in results:
        interpretation = r.get('clinical_interpretation', {})
        writer.writerow([
            r.get('file_name', ''),
            r.get('status', ''),
            r.get('prediction', ''),
            r.get('prediction_code', ''),
            r.get('confidence', ''),
            r.get('signal_quality', ''),
            interpretation.get('clinical_significance', ''),
            interpretation.get('urgency', ''),
            r.get('error', '')
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename=batch_results_{batch_id}.csv'
        }
    )


@router.get("/api/batch/{batch_id}/export/json")
async def export_batch_json(
    batch_id: str,
    status_filter: Optional[str] = Query(None)
):
    """
    Export batch results as JSON.
    
    Includes complete structured results for each file.
    """
    result = batch_processor.get_batch_result(batch_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    # Apply filter if specified
    results = result['results']
    if status_filter:
        results = [r for r in results if r.get('status') == status_filter]
    
    export_data = {
        'batch_id': batch_id,
        'export_timestamp': result.get('timestamp'),
        'total_files': len(results),
        'results': results
    }
    
    return JSONResponse(
        content=export_data,
        headers={
            'Content-Disposition': f'attachment; filename=batch_results_{batch_id}.json'
        }
    )


@router.get("/api/batch/{batch_id}/filter")
async def filter_batch_results(
    batch_id: str,
    status: Optional[str] = Query(None),
    prediction: Optional[str] = Query(None)
):
    """
    Filter batch results by status or prediction.
    """
    result = batch_processor.get_batch_result(batch_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    filtered = batch_processor.filter_results(batch_id, status, prediction)
    
    return {
        'batch_id': batch_id,
        'filter': {
            'status': status,
            'prediction': prediction
        },
        'total_filtered': len(filtered),
        'results': filtered
    }

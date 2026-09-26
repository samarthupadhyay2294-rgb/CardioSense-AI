"""
Batch ECG Processing Service

This service provides batch processing capabilities for multiple ECG files.
It reuses the existing single-file processing pipeline from ecg_service.
"""

import asyncio
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from app.services.ecg_service import process_ecg_file, save_uploaded_file
from app.core.config import settings

logger = logging.getLogger(__name__)


class BatchECGProcessor:
    """
    Process multiple ECG files in batch.
    
    Reuses the existing single-file processing pipeline:
    - File validation
    - Signal loading
    - Preprocessing
    - Feature extraction
    - ML prediction
    - Clinical interpretation
    """
    
    def __init__(self, max_workers: int = 2):
        self.max_workers = max_workers
        self.batch_results: Dict[str, Dict] = {}
    
    async def process_batch(
        self,
        files_data: List[tuple],  # List of (file_content, filename) tuples
        batch_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a batch of ECG files.
        
        Args:
            files_data: List of (file_content, filename) tuples
            batch_id: Optional batch identifier (generated if not provided)
        
        Returns:
            Batch processing results
        """
        if batch_id is None:
            batch_id = str(uuid.uuid4())
        
        total_files = len(files_data)
        results = []
        successful = 0
        failed = 0
        
        logger.info(f"Starting batch processing: {batch_id}, {total_files} files")
        
        # Process files sequentially (bounded concurrency)
        for idx, (file_content, filename) in enumerate(files_data):
            try:
                logger.info(f"Processing file {idx + 1}/{total_files}: {filename}")
                
                # Save file
                file_path = save_uploaded_file(file_content, filename)
                
                # Process using existing single-file pipeline
                result = await process_ecg_file(file_path, filename)
                
                # Add file metadata
                result['file_name'] = filename
                result['status'] = 'success'
                result['batch_id'] = batch_id
                
                results.append(result)
                successful += 1
                
                logger.info(f"Successfully processed: {filename}")
                
            except Exception as e:
                logger.error(f"Failed to process {filename}: {e}")
                
                results.append({
                    'file_name': filename,
                    'status': 'failed',
                    'error': str(e),
                    'error_type': self._classify_error(e),
                    'batch_id': batch_id
                })
                failed += 1
        
        batch_result = {
            'batch_id': batch_id,
            'total_files': total_files,
            'successful': successful,
            'failed': failed,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
        
        # Store batch results
        self.batch_results[batch_id] = batch_result
        
        logger.info(f"Batch processing complete: {batch_id}, {successful}/{total_files} successful")
        
        return batch_result
    
    def _classify_error(self, error: Exception) -> str:
        """Classify error type for user-friendly reporting."""
        error_msg = str(error).lower()
        
        if 'unsupported' in error_msg or 'format' in error_msg:
            return 'unsupported_format'
        elif 'signal' in error_msg or 'channel' in error_msg:
            return 'invalid_signal'
        elif 'lead' in error_msg:
            return 'invalid_lead_count'
        elif 'sampling' in error_msg:
            return 'invalid_sampling_rate'
        elif 'empty' in error_msg or 'size' in error_msg:
            return 'empty_file'
        elif 'memory' in error_msg:
            return 'memory_error'
        else:
            return 'processing_error'
    
    def get_batch_result(self, batch_id: str) -> Optional[Dict]:
        """Retrieve batch processing results."""
        return self.batch_results.get(batch_id)
    
    def filter_results(
        self,
        batch_id: str,
        status_filter: Optional[str] = None,
        prediction_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Filter batch results by status or prediction.
        
        Args:
            batch_id: Batch identifier
            status_filter: Filter by status ('success', 'failed')
            prediction_filter: Filter by prediction code
        
        Returns:
            Filtered results
        """
        batch_result = self.get_batch_result(batch_id)
        if not batch_result:
            return []
        
        results = batch_result['results']
        
        if status_filter:
            results = [r for r in results if r.get('status') == status_filter]
        
        if prediction_filter:
            results = [r for r in results if r.get('prediction_code') == prediction_filter]
        
        return results


# Global instance
batch_processor = BatchECGProcessor(max_workers=2)

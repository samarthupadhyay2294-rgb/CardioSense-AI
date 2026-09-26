import pytest
from app.services.batch_processing import batch_processor


class TestBatchECGProcessor:
    """Test the batch ECG processor."""
    
    def test_initialization(self):
        """Test processor initialization."""
        assert batch_processor is not None
        assert hasattr(batch_processor, 'max_workers')
        assert hasattr(batch_processor, 'batch_results')
    
    def test_error_classification(self):
        """Test error classification."""
        # Test different error types
        error = ValueError("Unsupported file format")
        error_type = batch_processor._classify_error(error)
        assert error_type in ['unsupported_format', 'invalid_signal', 'invalid_lead_count', 
                            'invalid_sampling_rate', 'empty_file', 'memory_error', 'processing_error']
        
        error = ValueError("Invalid signal channels")
        error_type = batch_processor._classify_error(error)
        assert error_type == 'invalid_signal'
        
        error = ValueError("Invalid lead count")
        error_type = batch_processor._classify_error(error)
        assert error_type == 'invalid_lead_count'
        
        error = ValueError("Empty file")
        error_type = batch_processor._classify_error(error)
        assert error_type == 'empty_file'
    
    def test_get_batch_result_not_found(self):
        """Test getting non-existent batch result."""
        result = batch_processor.get_batch_result("nonexistent_id")
        assert result is None
    
    def test_filter_results_not_found(self):
        """Test filtering results for non-existent batch."""
        results = batch_processor.filter_results("nonexistent_id")
        assert results == []
    
    def test_filter_results_empty(self):
        """Test filtering with no results."""
        # Create a mock batch with empty results
        batch_processor.batch_results["test_id"] = {
            'batch_id': 'test_id',
            'results': []
        }
        
        results = batch_processor.filter_results("test_id")
        assert results == []
    
    def test_filter_results_by_status(self):
        """Test filtering by status."""
        # Create mock batch results
        batch_processor.batch_results["test_id"] = {
            'batch_id': 'test_id',
            'results': [
                {'file_name': 'file1.csv', 'status': 'success', 'prediction_code': 'NORM'},
                {'file_name': 'file2.csv', 'status': 'failed', 'error': 'test'},
                {'file_name': 'file3.csv', 'status': 'success', 'prediction_code': 'MI'}
            ]
        }
        
        # Filter by success
        results = batch_processor.filter_results("test_id", status_filter='success')
        assert len(results) == 2
        assert all(r['status'] == 'success' for r in results)
        
        # Filter by failed
        results = batch_processor.filter_results("test_id", status_filter='failed')
        assert len(results) == 1
        assert results[0]['status'] == 'failed'
    
    def test_filter_results_by_prediction(self):
        """Test filtering by prediction code."""
        batch_processor.batch_results["test_id"] = {
            'batch_id': 'test_id',
            'results': [
                {'file_name': 'file1.csv', 'status': 'success', 'prediction_code': 'NORM'},
                {'file_name': 'file2.csv', 'status': 'success', 'prediction_code': 'MI'},
                {'file_name': 'file3.csv', 'status': 'success', 'prediction_code': 'NORM'}
            ]
        }
        
        results = batch_processor.filter_results("test_id", prediction_filter='NORM')
        assert len(results) == 2
        assert all(r['prediction_code'] == 'NORM' for r in results)
    
    def test_filter_results_combined(self):
        """Test filtering by both status and prediction."""
        batch_processor.batch_results["test_id"] = {
            'batch_id': 'test_id',
            'results': [
                {'file_name': 'file1.csv', 'status': 'success', 'prediction_code': 'NORM'},
                {'file_name': 'file2.csv', 'status': 'failed', 'prediction_code': 'MI'},
                {'file_name': 'file3.csv', 'status': 'success', 'prediction_code': 'MI'}
            ]
        }
        
        results = batch_processor.filter_results("test_id", status_filter='success', prediction_filter='MI')
        assert len(results) == 1
        assert results[0]['prediction_code'] == 'MI'
        assert results[0]['status'] == 'success'

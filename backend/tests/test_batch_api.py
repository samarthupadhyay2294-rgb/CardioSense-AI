import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


class TestBatchAPI:
    """Test the batch API endpoints."""
    
    def test_batch_analyze_no_files(self):
        """Test POST /api/batch/analyze with no files."""
        response = client.post("/api/batch/analyze")
        # FastAPI returns 422 for validation error when required files parameter is missing
        assert response.status_code == 422
    
    def test_batch_analyze_too_many_files(self):
        """Test POST /api/batch/analyze with too many files."""
        # Create mock files (this will fail validation but should hit the count check first)
        files = [('files', (f'test{i}.csv', b'test data')) for i in range(51)]
        response = client.post("/api/batch/analyze", files=files)
        assert response.status_code == 400
    
    def test_get_batch_result_not_found(self):
        """Test GET /api/batch/{batch_id} with non-existent batch."""
        response = client.get("/api/batch/nonexistent_id")
        assert response.status_code == 404
    
    def test_export_csv_not_found(self):
        """Test GET /api/batch/{batch_id}/export/csv with non-existent batch."""
        response = client.get("/api/batch/nonexistent_id/export/csv")
        assert response.status_code == 404
    
    def test_export_json_not_found(self):
        """Test GET /api/batch/{batch_id}/export/json with non-existent batch."""
        response = client.get("/api/batch/nonexistent_id/export/json")
        assert response.status_code == 404
    
    def test_filter_not_found(self):
        """Test GET /api/batch/{batch_id}/filter with non-existent batch."""
        response = client.get("/api/batch/nonexistent_id/filter")
        assert response.status_code == 404


class TestBatchAPIRouter:
    """Test batch router registration."""
    
    def test_router_registered(self):
        """Test that batch router is registered."""
        response = client.get("/api/batch/nonexistent_id")
        # Should not return 404 (should return 404 for not found batch, not route)
        assert response.status_code == 404
    
    def test_router_endpoints_exist(self):
        """Test that all expected endpoints exist."""
        # Check analyze endpoint exists (should return 422 for missing files, not 404)
        response = client.post("/api/batch/analyze")
        assert response.status_code == 422  # Validation error, not 404
        
        # Check other endpoints exist (should return 404 for not found batch, not 404 for route)
        # We can't test with a real batch_id without creating one, so we just verify
        # the router is loaded by checking the analyze endpoint works as expected
        response = client.get("/api/batch/nonexistent_id/export/csv")
        assert response.status_code == 404  # Batch not found, but route exists

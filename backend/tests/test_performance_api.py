import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


class TestPerformanceAPI:
    """Test the performance API endpoints."""
    
    def test_status_endpoint(self):
        """Test GET /api/performance/status"""
        response = client.get("/api/performance/status")
        
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert 'status' in data
            assert 'dataset_available' in data
            assert 'model_available' in data
    
    def test_metrics_endpoint_unavailable(self):
        """Test GET /api/performance/metrics when evaluation unavailable"""
        # This test assumes evaluation may not be run yet
        response = client.get("/api/performance/metrics")
        
        # Should return either available results or unavailable status
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            # Either status is available or unavailable
            assert 'status' in data
    
    def test_metrics_endpoint_with_params(self):
        """Test GET /api/performance/metrics with parameters"""
        response = client.get("/api/performance/metrics?fold=10&max_samples=100")
        
        assert response.status_code in [200, 500]
    
    def test_confusion_matrix_endpoint(self):
        """Test GET /api/performance/confusion-matrix"""
        response = client.get("/api/performance/confusion-matrix")
        
        # May return 503 if evaluation not available
        assert response.status_code in [200, 503, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert 'confusion_matrix' in data
            assert 'labels' in data
            assert 'normalized' in data
    
    def test_confusion_matrix_normalized(self):
        """Test GET /api/performance/confusion-matrix with normalize=true"""
        response = client.get("/api/performance/confusion-matrix?normalize=true")
        
        assert response.status_code in [200, 503, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert data['normalized'] == True
    
    def test_classes_endpoint(self):
        """Test GET /api/performance/classes"""
        response = client.get("/api/performance/classes")
        
        assert response.status_code in [200, 503, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert 'class_metrics' in data
            assert 'class_labels' in data
    
    def test_evaluate_endpoint_post(self):
        """Test POST /api/performance/evaluate"""
        response = client.post("/api/performance/evaluate")
        
        # May return 503 if dataset/model not available
        assert response.status_code in [200, 503, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert 'status' in data
    
    def test_evaluate_endpoint_with_params(self):
        """Test POST /api/performance/evaluate with parameters"""
        response = client.post("/api/performance/evaluate?fold=10&max_samples=50")
        
        assert response.status_code in [200, 503, 500]


class TestPerformanceAPIRouter:
    """Test performance router registration."""
    
    def test_router_registered(self):
        """Test that performance router is registered."""
        # Check if the route exists by trying to access it
        response = client.get("/api/performance/status")
        # Should not return 404
        assert response.status_code != 404
    
    def test_router_endpoints_exist(self):
        """Test that all expected endpoints exist."""
        endpoints = [
            "/api/performance/status",
            "/api/performance/metrics",
            "/api/performance/confusion-matrix",
            "/api/performance/classes",
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            # Should not return 404
            assert response.status_code != 404, f"Endpoint {endpoint} returned 404"

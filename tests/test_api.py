import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_and_model_metrics():
    response = client.get("/model/metrics")
    assert response.status_code == 200

import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}

def test_webhook_verification():
    # Simulate a correct verification request
    params = {
        'hub.mode': 'subscribe',
        'hub.verify_token': 'your_verification_token_here',
        'hub.challenge': 'test_challenge'
    }
    response = client.get("/webhook", params=params)
    assert response.status_code == 200
    assert response.text == 'test_challenge'

    # Simulate an incorrect verification request
    params['hub.verify_token'] = 'wrong_token'
    response = client.get("/webhook", params=params)
    assert response.status_code == 404

def test_analyze_video_no_data(monkeypatch):
    # Patch data_collector.process_video_data to return False
    from src.main import data_collector
    monkeypatch.setattr(data_collector, "process_video_data", lambda video_id: False)
    response = client.post("/analyze/test_video_id")
    assert response.status_code == 200
    assert response.json()["status"] == "error"
    assert "Failed to collect video data" in response.json()["message"]

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_chat():
    response = client.post(
        "/api/chat",
        json={
            "session_id": "test-1",
            "message": "What is the refund policy?"
        }
    )
    assert response.status_code == 200
    body = response.json()
    assert "answer" in body
    assert "source" in body
    assert "escalated" in body

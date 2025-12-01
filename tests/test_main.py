from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Teste 1: Verifica se a API liga e responde na raiz"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_ask_endpoint_structure():
    """Teste 2: Verifica se o endpoint /ask aceita o JSON correto"""
    # Mesmo sem API Key, ele deve responder (com o mock ou erro tratado), mas não 500 ou 422
    payload = {
        "question": "O que é EC2?",
        "subject": "AWS Cloud"
    }
    response = client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["question"] == "O que é EC2?"
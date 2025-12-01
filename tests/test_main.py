from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    """Teste 1: Verifica se o Frontend (HTML) carrega na raiz"""
    response = client.get("/")
    
    # Verifica se deu sucesso (200 OK)
    assert response.status_code == 200
    
    # Verifica se é HTML mesmo (procura o título do site no código)
    # Não usamos .json() aqui porque agora é um site, não uma API pura na raiz
    assert "IsCoolGPT" in response.text

def test_ask_endpoint_structure():
    """Teste 2: Verifica se o endpoint /ask aceita o JSON correto"""
    payload = {
        "question": "O que é EC2?",
        "subject": "AWS Cloud"
    }
    response = client.post("/ask", json=payload)
    
    # O teste deve garantir que a rota existe e aceita os dados.
    # Se der 200 (sucesso) ou 500 (erro de chave API), significa que a rota existe.
    # Se der 404 ou 422, aí sim é falha de estrutura.
    assert response.status_code != 404
    assert response.status_code != 422
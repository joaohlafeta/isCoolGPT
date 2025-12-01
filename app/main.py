from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import uvicorn
import google.generativeai as genai

# Inicialização da App
app = FastAPI(
    title="IsCoolGPT API",
    description="Backend do Assistente Inteligente de Estudos em Cloud Computing",
    version="1.0.0"
)

# Modelo de Dados para Request
class StudentQuery(BaseModel):
    question: str
    subject: str = "Cloud Computing"

def get_llm_response(query: str, subject: str) -> str:
    """
    Função que chama o Google Gemini.
    Requer a variável de ambiente GOOGLE_API_KEY.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    
    # Fallback para caso a chave não esteja configurada (evita crash no deploy inicial)
    if not api_key:
        print("AVISO: GOOGLE_API_KEY não encontrada. Usando resposta simulada.")
        return f"[MODO SIMULADO] A resposta para '{query}' sobre '{subject}' envolve escalabilidade e AWS. (Configure a API Key para respostas reais)"

    try:
        # Configura o Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # Cria o prompt contextualizado
        prompt = f"Você é um tutor universitário especialista na disciplina de {subject}. Responda de forma didática, técnica e resumida (máximo 1 parágrafo) à pergunta do aluno: {query}"
        
        # Gera a resposta
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Erro ao chamar Gemini: {e}")
        return "Desculpe, o assistente inteligente está indisponível no momento. Verifique os logs do servidor."

@app.get("/")
def health_check():
    """Rota para verificar se a API está online (Health Check do Load Balancer)"""
    return {"status": "healthy", "service": "IsCoolGPT", "version": "1.0.0"}

@app.post("/ask")
def ask_assistant(query: StudentQuery):
    """Endpoint principal de interação com o aluno"""
    try:
        response_text = get_llm_response(query.question, query.subject)
        return {
            "question": query.question,
            "subject": query.subject,
            "answer": response_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
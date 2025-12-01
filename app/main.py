from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
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

# Configuração de CORS (Para permitir que o frontend fale com o backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de Dados para Request
class StudentQuery(BaseModel):
    question: str
    subject: str = "Cloud Computing"

# --- LÓGICA DO GEMINI (IA) ---
def get_llm_response(query: str, subject: str) -> str:
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("ERRO: GOOGLE_API_KEY não encontrada.")
        return "Erro de Configuração: A chave da API do Google (GOOGLE_API_KEY) não foi encontrada no servidor. Verifique a Task Definition no ECS."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"Você é um tutor universitário especialista na disciplina de {subject}. O aluno perguntou: '{query}'. Responda de forma didática, técnica e direta (máximo 150 palavras)."
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Erro ao chamar Gemini: {e}")
        return f"Erro ao processar sua pergunta: {str(e)}"

# --- ROTAS DA API ---

@app.post("/ask")
def ask_assistant(query: StudentQuery):
    try:
        response_text = get_llm_response(query.question, query.subject)
        return {
            "question": query.question,
            "subject": query.subject,
            "answer": response_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- FRONTEND (O SITE) ---
# Aqui colocamos o HTML/CSS/JS direto no Python para facilitar o deploy (Single File)

html_content = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IsCoolGPT - Assistente Cloud</title>
    <style>
        :root { --primary: #2563eb; --bg: #f3f4f6; --chat-bg: #ffffff; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: var(--bg); margin: 0; display: flex; flex-direction: column; height: 100vh; }
        header { background-color: var(--primary); color: white; padding: 1rem; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { margin: 0; font-size: 1.5rem; }
        #chat-container { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 15px; max-width: 800px; margin: 0 auto; width: 100%; box-sizing: border-box; }
        .message { padding: 15px; border-radius: 10px; max-width: 80%; line-height: 1.5; animation: fadeIn 0.3s ease; }
        .user-msg { background-color: var(--primary); color: white; align-self: flex-end; border-bottom-right-radius: 2px; }
        .bot-msg { background-color: var(--chat-bg); color: #333; align-self: flex-start; border-bottom-left-radius: 2px; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }
        .error-msg { background-color: #fee2e2; color: #991b1b; align-self: center; }
        #input-area { background-color: white; padding: 20px; box-shadow: 0 -2px 10px rgba(0,0,0,0.05); display: flex; gap: 10px; max-width: 800px; margin: 0 auto; width: 100%; box-sizing: border-box; }
        input { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 25px; outline: none; transition: border-color 0.3s; }
        input:focus { border-color: var(--primary); }
        button { background-color: var(--primary); color: white; border: none; padding: 10px 25px; border-radius: 25px; cursor: pointer; font-weight: bold; transition: background 0.2s; }
        button:hover { background-color: #1d4ed8; }
        button:disabled { background-color: #9ca3af; cursor: not-allowed; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .loading { font-style: italic; color: #666; font-size: 0.9rem; }
    </style>
</head>
<body>
    <header>
        <h1>☁️ IsCoolGPT - Assistente de Cloud</h1>
    </header>
    
    <div id="chat-container">
        <div class="message bot-msg">
            Olá! Sou seu assistente de Cloud Computing. Em que posso ajudar hoje?
        </div>
    </div>

    <div id="input-area">
        <input type="text" id="question" placeholder="Digite sua dúvida sobre AWS, Docker, etc..." onkeypress="handleEnter(event)">
        <button onclick="sendMessage()" id="sendBtn">Enviar</button>
    </div>

    <script>
        async function sendMessage() {
            const input = document.getElementById('question');
            const btn = document.getElementById('sendBtn');
            const chat = document.getElementById('chat-container');
            const text = input.value.trim();

            if (!text) return;

            // Adiciona mensagem do usuário
            appendMessage(text, 'user-msg');
            input.value = '';
            input.disabled = true;
            btn.disabled = true;
            btn.innerText = 'Pensando...';

            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question: text, subject: "Cloud Computing" })
                });

                const data = await response.json();
                
                if (response.ok) {
                    appendMessage(data.answer, 'bot-msg');
                } else {
                    appendMessage("Erro: " + (data.detail || "Falha desconhecida"), 'error-msg');
                }
            } catch (error) {
                appendMessage("Erro de conexão. O servidor pode estar offline.", 'error-msg');
            } finally {
                input.disabled = false;
                btn.disabled = false;
                btn.innerText = 'Enviar';
                input.focus();
            }
        }

        function appendMessage(text, className) {
            const chat = document.getElementById('chat-container');
            const div = document.createElement('div');
            div.className = `message ${className}`;
            div.innerText = text;
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }

        function handleEnter(e) {
            if (e.key === 'Enter') sendMessage();
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def read_root():
    return html_content

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

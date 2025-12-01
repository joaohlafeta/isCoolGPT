# --- Estágio 1: Builder (Compilação e Dependências) ---
FROM python:3.10-slim as builder

WORKDIR /app

# Variáveis de ambiente para evitar arquivos .pyc e logs em buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala dependências do sistema necessárias para compilação (se houver)
RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Instala dependências Python em um diretório virtual
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --target=/app/dependencies -r requirements.txt

# --- Estágio 2: Runner (Imagem Final Leve) ---
FROM python:3.10-slim

WORKDIR /app

# Variáveis de ambiente
ENV PYTHONPATH=/app/dependencies
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copia apenas as bibliotecas instaladas do estágio anterior
COPY --from=builder /app/dependencies /app/dependencies

# Copia o código fonte da aplicação
COPY app /app/app

# Cria um usuário não-root para segurança (Boas práticas DevOps)
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Expõe a porta que o FastAPI usa
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
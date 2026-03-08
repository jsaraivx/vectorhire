#!/bin/bash

echo "========================================="
echo " Iniciando VectorHire ATS (Mac/Linux)"
echo "========================================="

echo "\n[1/2] Subindo o Banco Vetorial (PostgreSQL + pgvector)..."
docker-compose up -d

echo "\n[2/2] Iniciando o Servidor de Inteligência Artificial (FastAPI)..."
echo "O Backend estará rodando em: http://127.0.0.1:8000"
echo "Pressione CTRL+C para encerrar."

# Verifica se o ambiente virtual (venv) está ativo, se não, usa o python global do contexto
if [[ "$VIRTUAL_ENV" != "" ]]; then
    uvicorn src.api.app:app --reload --port 8000
else
    # Tenta usar run uv, poetry ou fallback pro python se o usuário não ativou
    python3 -m uvicorn src.api.app:app --reload --port 8000
fi

#!/bin/bash

echo "========================================="
echo " Destruindo ambiente VectorHire ATS (Mac/Linux)"
echo "========================================="

echo "\nDerrubando banco de dados e limpando volumes (pgvector)..."
docker-compose down -v

echo "\nLimpando sessão de extração em disco (data/raw e data/processed)..."
rm -rf data/raw
rm -rf data/processed

# O Uvicorn (FastAPI) geralmente é fechado com CTRL+C no terminal onde o start.sh foi rodado.
# Como fallback, encerra qualquer processo rodando na porta 8000:
echo "\nEncerrando possível instância do FastAPI rodando em background (porta 8000)..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "Nenhum servidor rodando na porta 8000."

echo "\n✅ Ambiente destruído com sucesso."

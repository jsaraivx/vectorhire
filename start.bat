@echo off
echo =========================================
echo  Iniciando VectorHire ATS (Windows)
echo =========================================

echo.
echo [1/2] Subindo o Banco Vetorial (PostgreSQL + pgvector)...
docker-compose up -d

echo.
echo [2/2] Iniciando o Servidor de Inteligência Artificial (FastAPI)...
echo O Backend estara rodando em: http://127.0.0.1:8000
echo Pressione CTRL+C para encerrar.

rem Verifica se existe a pasta venv para usar o ambiente virtual
if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe -m uvicorn src.api.app:app --reload --port 8000
) else (
    python -m uvicorn src.api.app:app --reload --port 8000
)
pause

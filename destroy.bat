@echo off
echo =========================================
echo  Destruindo ambiente VectorHire ATS (Windows)
echo =========================================

echo.
echo Derrubando banco de dados e limpando volumes (pgvector)...
docker-compose down -v

echo.
echo Limpando sessao de extracao em disco (data/raw e data/processed)...
if exist "data\raw" rmdir /s /q "data\raw"
if exist "data\processed" rmdir /s /q "data\processed"

rem O Uvicorn (FastAPI) geralmente eh fechado com CTRL+C no terminal onde o start.bat foi rodado.
rem Como fallback, tenta encerrar processo vinculado aa porta 8000:
echo.
echo Procurando por servidor na porta 8000 (Pode demorar uns segundos)...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do taskkill /F /PID %%a 2>nul

echo.
echo ✅ Ambiente destruido com sucesso.
pause

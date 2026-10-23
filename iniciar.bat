@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === EduMindAI - iniciando ===
if not exist .venv (
  echo Criando ambiente Python...
  python -m venv .venv
)
call .venv\Scripts\activate.bat
echo Instalando dependencias - a primeira vez demora...
pip install -q -r requirements-ia.txt
if not exist edumindai.db (
  echo Criando banco com dados FICTICIOS de demonstracao...
  python -m app.seed
)
echo.
echo Abra no navegador: http://localhost:8000
echo Em outro aparelho no mesmo Wi-Fi: http://IP-DESTE-PC:8000 - veja o IP com ipconfig
echo Senha dos usuarios de demonstracao: edumind123
echo Para parar: feche esta janela ou aperte Ctrl+C
echo.
uvicorn app.main:app --host 0.0.0.0 --port 8000
pause

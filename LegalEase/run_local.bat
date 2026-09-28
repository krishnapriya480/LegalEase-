@echo off
if not exist .venv (
    py -3 -m venv .venv
)
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
start "LegalEase API" cmd /k "call .venv\Scripts\activate && uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000"
timeout /t 3 >nul
start "LegalEase UI" cmd /k "call .venv\Scripts\activate && streamlit run frontend\app.py"

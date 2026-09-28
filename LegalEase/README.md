# LegalEase — AI-Powered Legal Document Generator

LegalEase is a FastAPI + Streamlit application for generating editable legal-document drafts with Gemini and exporting them as TXT, DOCX, or PDF.

## Features

- Employment contracts, NDAs, lease agreements, offer letters, service contracts, and custom agreements.
- Gemini-powered draft generation.
- Editable preview in Streamlit.
- DOCX export with title, terms table, logo, and footer.
- PDF export with logo/header/footer.
- TXT export.
- FastAPI `/generate` endpoint and `/health` endpoint.
- Configurable Gemini model through `.env`.
- Optional `DEMO_MODE=true` for testing the UI without an API key.

> Legal notice: LegalEase generates drafts for informational/document-preparation purposes. It is not a law firm and does not provide legal advice. Generated documents should be reviewed by a qualified lawyer before use, especially where local law or significant rights/obligations are involved.

## Project structure

```text
LegalEase/
├── ai_core/
│   ├── __init__.py
│   └── gemini_generator.py
├── backend/
│   ├── __init__.py
│   ├── main.py
│   └── routes.py
├── frontend/
│   ├── __init__.py
│   └── app.py
├── utils/
│   ├── __init__.py
│   ├── document_formatter.py
│   └── text_utils.py
├── assets/
│   └── logo.png
├── tests/
│   ├── __init__.py
│   └── test_smoke.py
├── .env.example
├── .gitignore
├── Dockerfile
├── Procfile
├── README.md
├── requirements.txt
└── run_local.bat
```

## 1. Prerequisites

- Python 3.10+
- VS Code
- A Gemini API key if using live AI generation.

The project specification calls for FastAPI, Streamlit, Gemini, python-docx, fpdf, Pillow, requests and python-dotenv.

## 2. Create the environment

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Windows PowerShell

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Configure Gemini

```bash
cp .env.example .env
```

On Windows, copy `.env.example` to `.env` manually.

Set:

```env
GEMINI_API_KEY=YOUR_REAL_KEY
GEMINI_MODEL=gemini-3.8-flash
DEMO_MODE=false
BACKEND_URL=http://127.0.0.1:8000
```

The model is deliberately configurable. If your account supports another Gemini model, change only `GEMINI_MODEL`.

## 4. Run the backend

From the project root:

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Check:

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/docs
```

## 5. Run the frontend

Open a second terminal, activate the same virtual environment, then:

```bash
streamlit run frontend/app.py
```

Open the URL shown by Streamlit, normally:

```text
http://localhost:8501
```

## 6. Demo mode

If you want to test the complete UI and export pipeline without a Gemini API key:

```env
DEMO_MODE=true
```

The application then uses a clearly labeled local draft generator. Set it back to `false` for live Gemini generation.

## 7. Test

Run:

```bash
python -m unittest discover -s tests -v
```

The included smoke tests validate imports, sanitization, and export generation.

## 8. API example

```bash
curl -X POST "http://127.0.0.1:8000/generate"   -H "Content-Type: application/json"   -d '{
    "document_type": "Non-Disclosure Agreement",
    "parties": "Jane Doe (Disclosing Party), TechNova Inc. (Receiving Party)",
    "terms": "Confidentiality; No unauthorized disclosure; Return confidential information upon termination",
    "effective_date": "September 26, 2026"
  }'
```

## Notes

The original project document describes `gemini-1.5-pro`; that model name is kept as a supported configuration concept, but the default in this implementation is configurable and set to a current Gemini model so the project does not depend on an obsolete SDK/model pairing.

This implementation intentionally does not claim that AI-generated text is legally valid for a particular jurisdiction.

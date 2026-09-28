from __future__ import annotations

import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ai_core.gemini_generator import GeminiDocumentGenerator

router = APIRouter()


class DocumentRequest(BaseModel):
    document_type: str = Field(..., min_length=2, max_length=120)
    parties: str = Field(..., min_length=2, max_length=3000)
    terms: str = Field(..., min_length=2, max_length=10000)
    effective_date: str = Field(..., min_length=2, max_length=100)


class DocumentResponse(BaseModel):
    document_type: str
    content: str
    mode: str
    model: str


def get_generator() -> GeminiDocumentGenerator:
    return GeminiDocumentGenerator()


@router.get("/health", tags=["health"])
def health():
    demo = os.getenv("DEMO_MODE", "false").lower() in {"1", "true", "yes", "on"}
    return {
        "status": "ok",
        "demo_mode": demo,
        "model": os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
    }


@router.post("/generate", response_model=DocumentResponse, tags=["generation"])
def generate_document(payload: DocumentRequest):
    try:
        generator = get_generator()
        content = generator.generate_document(
            document_type=payload.document_type,
            parties=payload.parties,
            terms=payload.terms,
            effective_date=payload.effective_date,
        )
        mode = "demo" if generator.demo_mode else "gemini"
        return DocumentResponse(
            document_type=payload.document_type,
            content=content,
            mode=mode,
            model=generator.model,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected generation error: {exc}",
        ) from exc

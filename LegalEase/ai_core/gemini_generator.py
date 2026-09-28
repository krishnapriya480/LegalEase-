from __future__ import annotations

import os
from datetime import date
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


class GeminiDocumentGenerator:
    """Generate legal-document drafts using Google's current Gemini Python SDK."""

    def __init__(self, model: Optional[str] = None) -> None:
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.demo_mode = os.getenv("DEMO_MODE", "false").strip().lower() in {
            "1", "true", "yes", "on"
        }

        self.client = None
        if not self.demo_mode and self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as exc:
                raise RuntimeError(
                    "Unable to initialize the Gemini client. "
                    "Check the google-genai installation and GEMINI_API_KEY."
                ) from exc

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
    ) -> str:
        document_type = document_type.strip()
        parties = parties.strip()
        terms = terms.strip()
        effective_date = effective_date.strip()

        if not all([document_type, parties, terms, effective_date]):
            raise ValueError("document_type, parties, terms and effective_date are required.")

        if self.demo_mode:
            return self._demo_document(document_type, parties, terms, effective_date)

        if not self.client:
            raise RuntimeError(
                "Gemini is not configured. Add GEMINI_API_KEY to .env, "
                "or set DEMO_MODE=true for local testing."
            )

        prompt = self._build_prompt(
            document_type=document_type,
            parties=parties,
            terms=terms,
            effective_date=effective_date,
        )

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            generated = getattr(response, "text", None)
            if not generated:
                raise RuntimeError("Gemini returned an empty response.")
            return generated.strip()
        except Exception as exc:
            raise RuntimeError(f"Gemini generation failed: {exc}") from exc

    @staticmethod
    def _build_prompt(
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
    ) -> str:
        return f"""
You are a professional legal-document drafting assistant.

Create a clear, structured DRAFT of a {document_type}.

Inputs:
- Parties: {parties}
- Effective date: {effective_date}
- User-supplied terms: {terms}

Requirements:
1. Use a professional legal-document structure.
2. Include a clear title.
3. Identify the parties and effective date.
4. Convert the supplied terms into sensible sections/clauses without inventing
   material facts that were not provided.
5. Use placeholders such as [INSERT ...] when an important detail is missing.
6. Include signature blocks where appropriate.
7. Do not claim the document is legally valid in any particular jurisdiction.
8. Do not fabricate statutes, case law, registration numbers, addresses,
   monetary values, or other facts.
9. Return plain text with headings; do not use Markdown tables.
10. End with a short "Review Notice" stating that the draft should be reviewed
    by a qualified legal professional before execution.

This is a document-generation task, not a request for legal advice.
""".strip()

    @staticmethod
    def _demo_document(
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
    ) -> str:
        terms_list = [
            item.strip(" .")
            for item in terms.split(";")
            if item.strip()
        ]
        term_lines = "\n".join(
            f"{index}. {item}" for index, item in enumerate(terms_list, start=1)
        )

        return f"""DRAFT {document_type.upper()}

Effective Date
{effective_date}

PARTIES
{parties}

PURPOSE
This draft records the principal terms supplied by the user for the
{document_type}.

TERMS AND CONDITIONS
{term_lines or "1. [INSERT TERMS]"}

GENERAL PROVISIONS
1. The parties should verify all names, dates, addresses, amounts, obligations,
   governing-law provisions, and other material details before execution.
2. Any missing information should be completed before the document is signed.
3. This draft is generated for document-preparation and informational purposes.

SIGNATURES

Party 1: ______________________________
Name: ________________________________
Date: _________________________________

Party 2: ______________________________
Name: ________________________________
Date: _________________________________

REVIEW NOTICE
This is an AI-assisted draft and is not legal advice. A qualified legal
professional should review the document for the applicable jurisdiction and
specific circumstances before execution.

Generated on: {date.today().isoformat()}
"""

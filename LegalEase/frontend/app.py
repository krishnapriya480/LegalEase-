from __future__ import annotations

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import date

import requests
import streamlit as st
from dotenv import load_dotenv

from utils.document_formatter import format_docx, format_pdf, format_txt
from utils.text_utils import sanitize_text, text_to_html

load_dotenv()

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")

st.markdown(
    """
    <style>
    .main-title { text-align:center; font-size:2.5rem; font-weight:700; margin-bottom:0; }
    .subtitle { text-align:center; color:#777; margin-top:0.25rem; }
    .legal-card {
        background:#101418; color:#f3f4f6; padding:1.4rem; border-radius:14px;
        border:1px solid #30363d; max-height:620px; overflow-y:auto;
        font-family: Georgia, "Times New Roman", serif; line-height:1.65;
    }
    .notice { padding:0.8rem 1rem; border-radius:10px; background:#fff7e6; }
    </style>
    """,
    unsafe_allow_html=True,
)

if "document" not in st.session_state:
    st.session_state.document = ""
if "doc_type" not in st.session_state:
    st.session_state.doc_type = "Employment Contract"

st.markdown('<div class="main-title">⚖️ LegalEase</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">AI-Powered Legal Document Drafting Assistant</div>',
    unsafe_allow_html=True,
)

st.warning(
    "LegalEase creates AI-assisted drafts for informational/document-preparation purposes. "
    "It is not legal advice. Review important documents with a qualified legal professional."
)

with st.sidebar:
    st.header("Document Inputs")

    doc_type = st.selectbox(
        "Document type",
        [
            "Employment Contract",
            "Non-Disclosure Agreement",
            "Lease Agreement",
            "Employment Offer Letter",
            "Freelance Work Contract",
            "Service Agreement",
            "General Agreement",
            "Custom Legal Document",
        ],
        index=0,
    )

    parties = st.text_area(
        "Parties involved",
        placeholder="Jane Doe (Service Provider), TechNova Inc. (Client)",
        height=100,
    )

    terms = st.text_area(
        "Terms & conditions",
        placeholder=(
            "Payment within 30 days of invoice; "
            "Confidentiality must be maintained; "
            "Either party may terminate with 15 days notice"
        ),
        height=160,
        help="Separate clauses with semicolons.",
    )

    effective_date = st.text_input(
        "Effective date",
        value=date.today().strftime("%B %d, %Y"),
    )

    st.caption(f"Backend: {BACKEND_URL}")

    if st.button("Check backend", use_container_width=True):
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=5)
            response.raise_for_status()
            info = response.json()
            st.success(f"Backend OK • mode={info.get('demo_mode')} • model={info.get('model')}")
        except requests.RequestException as exc:
            st.error(f"Backend unavailable: {exc}")

    generate_clicked = st.button(
        "✨ Generate Document",
        type="primary",
        use_container_width=True,
    )

if generate_clicked:
    missing = []
    if not parties.strip():
        missing.append("parties")
    if not terms.strip():
        missing.append("terms")
    if not effective_date.strip():
        missing.append("effective date")

    if missing:
        st.error("Please provide: " + ", ".join(missing) + ".")
    else:
        payload = {
            "document_type": doc_type,
            "parties": parties,
            "terms": terms,
            "effective_date": effective_date,
        }
        with st.spinner("Generating your document..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/generate",
                    json=payload,
                    timeout=120,
                )
                if response.status_code >= 400:
                    try:
                        detail = response.json().get("detail", response.text)
                    except ValueError:
                        detail = response.text
                    raise RuntimeError(f"Backend error {response.status_code}: {detail}")

                data = response.json()
                st.session_state.document = sanitize_text(data["content"])
                st.session_state.doc_type = doc_type
                st.success(
                    f"Document generated using {data.get('mode', 'unknown')} mode."
                )
            except (requests.RequestException, RuntimeError) as exc:
                st.error(str(exc))

st.divider()

left, right = st.columns([1.2, 1])

with left:
    st.subheader("Document Preview")

    if st.session_state.document:
        preview_html = text_to_html(st.session_state.document)
        st.markdown(
            f'<div class="legal-card">{preview_html}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.info("Generate a document to see the formatted preview here.")

with right:
    st.subheader("Edit Document")

    edited = st.text_area(
        "Editable content",
        value=st.session_state.document,
        height=560,
        label_visibility="collapsed",
        placeholder="Generated document content will appear here.",
    )

    if st.button("Save edits", use_container_width=True):
        st.session_state.document = sanitize_text(edited)
        st.success("Edits saved to the current session.")

st.divider()
st.subheader("Download")

if st.session_state.document:
    content = sanitize_text(st.session_state.document)

    txt_data = format_txt(content)
    docx_data = format_docx(content, st.session_state.doc_type, terms)
    pdf_data = format_pdf(content, st.session_state.doc_type, terms)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button(
            "⬇️ Download TXT",
            data=txt_data,
            file_name="legalease_document.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with c2:
        st.download_button(
            "⬇️ Download DOCX",
            data=docx_data,
            file_name="legalease_document.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )
    with c3:
        st.download_button(
            "⬇️ Download PDF",
            data=pdf_data,
            file_name="legalease_document.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
else:
    st.caption("Download buttons become available after a document is generated.")

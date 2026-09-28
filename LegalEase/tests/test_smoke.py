import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.document_formatter import format_docx, format_pdf, format_txt
from utils.text_utils import sanitize_text, terms_from_string


class LegalEaseSmokeTests(unittest.TestCase):
    def test_sanitize_text(self):
        value = sanitize_text("“Hello” — world…")
        self.assertEqual(value, '"Hello" - world...')

    def test_terms(self):
        self.assertEqual(
            terms_from_string("Payment; Confidentiality; Termination"),
            ["Payment", "Confidentiality", "Termination"],
        )

    def test_txt_export(self):
        data = format_txt("Hello LegalEase")
        self.assertEqual(data, b"Hello LegalEase")

    def test_docx_export(self):
        data = format_docx(
            "EMPLOYMENT CONTRACT\n\nThis is a draft.",
            "Employment Contract",
            "Confidentiality; Payment",
        )
        self.assertTrue(data.startswith(b"PK"))
        self.assertGreater(len(data), 1000)

    def test_pdf_export(self):
        data = format_pdf(
            "EMPLOYMENT CONTRACT\n\nThis is a draft.",
            "Employment Contract",
            "Confidentiality; Payment",
        )
        self.assertTrue(data.startswith(b"%PDF"))
        self.assertGreater(len(data), 500)


if __name__ == "__main__":
    unittest.main()

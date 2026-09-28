from __future__ import annotations

import html
import re
import unicodedata


def sanitize_text(text: str) -> str:
    """Normalize typographic punctuation and remove unsafe control characters."""
    if not text:
        return ""

    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2212": "-",
        "\u00a0": " ",
        "\u2026": "...",
        "\u2022": "-",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)

    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)
    return text.strip()


def html_escape(text: str) -> str:
    return html.escape(sanitize_text(text))


def terms_from_string(terms: str) -> list[str]:
    return [
        item.strip(" \t\r\n.;")
        for item in terms.split(";")
        if item.strip(" \t\r\n.;")
    ]


def text_to_html(text: str) -> str:
    """Convert plain text into safe, readable HTML."""
    safe = html_escape(text)
    blocks = re.split(r"\n\s*\n", safe)
    rendered = []

    for block in blocks:
        lines = block.splitlines()
        if not lines:
            continue
        first = lines[0].strip()
        if (
            first.isupper()
            and len(first) <= 80
            and not first.endswith((".", ":", ";"))
        ):
            body = "<br>".join(lines[1:]).strip()
            rendered.append(f"<h3>{first}</h3><p>{body}</p>")
        else:
            rendered.append(f"<p>{'<br>'.join(lines)}</p>")

    return "\n".join(rendered)

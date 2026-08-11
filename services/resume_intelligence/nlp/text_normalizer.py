import re


def normalize_text(text):
    """Normalize extracted resume text for NLP and ATS processing."""

    if not text:
        return ""

    cleaned = text.replace("\x00", " ")
    cleaned = cleaned.replace("\r\n", "\n")
    cleaned = cleaned.replace("\r", "\n")
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()

import re
from functools import lru_cache

try:
    import spacy
except ImportError:  # pragma: no cover - optional dependency
    spacy = None

from services.resume_intelligence.config import MAX_NLP_TEXT_LENGTH, SPACY_MODEL


@lru_cache(maxsize=1)
def get_nlp():
    """Load the spaCy model once per application process."""

    if spacy is None:
        raise RuntimeError("spaCy is not installed. Run: pip install spacy")

    try:
        nlp = spacy.load(SPACY_MODEL)
    except OSError as exc:
        raise RuntimeError(
            f"spaCy model '{SPACY_MODEL}' is not installed. Run: python -m spacy download {SPACY_MODEL}"
        ) from exc

    nlp.max_length = max(nlp.max_length, MAX_NLP_TEXT_LENGTH + 1000)
    return nlp


def normalize_text(text):
    """Normalize extracted PDF/DOCX text before NLP processing."""

    if not text:
        return ""

    text = text.replace("\x00", " ")
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def process_text(text):
    """Return a processed spaCy document."""

    normalized = normalize_text(text)

    if not normalized:
        return None

    normalized = normalized[:MAX_NLP_TEXT_LENGTH]
    return get_nlp()(normalized)

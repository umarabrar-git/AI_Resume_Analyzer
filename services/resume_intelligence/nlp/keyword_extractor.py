import re

from services.resume_intelligence.nlp.skill_extractor import extract_skill_candidates


def extract_keywords(text, limit=30):
    """Extract keyword-style candidates from resume text.

    This is intentionally lightweight and meant to complement the existing
    skill extraction pipeline rather than replace it.
    """

    if not text:
        return []

    candidates = extract_skill_candidates(text)
    cleaned = []

    for candidate in candidates:
        value = re.sub(r"\s+", " ", (candidate or "").strip())
        if value and value not in cleaned:
            cleaned.append(value)

    return cleaned[:limit]

import re

from services.resume_intelligence.config import MAX_PHRASE_WORDS, MAX_SKILL_CANDIDATES
from services.resume_intelligence.nlp.nlp_service import process_text

SECTION_NOISE = {
    "resume",
    "curriculum vitae",
    "professional profile",
    "professional summary",
    "summary",
    "objective",
    "career objective",
    "work experience",
    "professional experience",
    "employment history",
    "education",
    "academic background",
    "skills",
    "technical skills",
    "core competencies",
    "projects",
    "certifications",
    "references",
    "contact information",
    "personal information",
}

NOISE_WORDS = {
    "i",
    "me",
    "my",
    "we",
    "our",
    "you",
    "your",
    "he",
    "she",
    "they",
    "them",
    "this",
    "that",
    "these",
    "those",
    "year",
    "years",
    "month",
    "months",
    "company",
    "organization",
    "resume",
    "cv",
}


def _clean_phrase(value):
    value = re.sub(r"\s+", " ", value or "")
    value = value.strip(" \t\n\r.,:;!?()[]{}<>|/\\")
    return value


def _candidate_key(value):
    return value.casefold()


def _valid_phrase(value):
    if not value:
        return False

    lowered = value.casefold()

    if lowered in SECTION_NOISE or lowered in NOISE_WORDS:
        return False

    words = value.split()

    if not words:
        return False

    if len(words) > MAX_PHRASE_WORDS:
        return False

    if len(value) < 2 or value.isdigit():
        return False

    if not any(character.isalpha() for character in value):
        return False

    return True


def _candidate_score(span):
    """Rank phrases by linguistic usefulness."""

    score = 0
    tokens = [token for token in span if not token.is_space]

    if not tokens:
        return 0

    if len(tokens) >= 2:
        score += 2

    if any(token.pos_ == "PROPN" for token in tokens):
        score += 2

    if any(token.pos_ in {"NOUN", "PROPN"} for token in tokens):
        score += 2

    if any(token.pos_ == "ADJ" for token in tokens):
        score += 1

    if all(token.is_stop for token in tokens):
        score -= 5

    return score


def extract_skill_candidates(text):
    """Extract ranked professional phrase candidates."""

    doc = process_text(text)

    if doc is None:
        return []

    candidates = {}

    for chunk in doc.noun_chunks:
        phrase = _clean_phrase(chunk.text)

        if not _valid_phrase(phrase):
            continue

        score = _candidate_score(chunk)

        if score <= 0:
            continue

        key = _candidate_key(phrase)
        existing = candidates.get(key)

        if existing is None or score > existing["score"]:
            candidates[key] = {"name": phrase, "score": score}

    for token in doc:
        if token.pos_ != "PROPN":
            continue

        if token.is_stop or token.like_email or token.like_url:
            continue

        phrase = _clean_phrase(token.text)

        if not _valid_phrase(phrase):
            continue

        key = _candidate_key(phrase)
        existing = candidates.get(key)

        if existing is None:
            candidates[key] = {"name": phrase, "score": 2}

    ranked = sorted(candidates.values(), key=lambda item: (-item["score"], item["name"].casefold()))
    return [item["name"] for item in ranked[:MAX_SKILL_CANDIDATES]]

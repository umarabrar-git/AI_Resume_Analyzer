import re

from services.resume_intelligence.nlp.nlp_service import process_text

TITLE_SUFFIXES = (
    "manager",
    "engineer",
    "developer",
    "analyst",
    "scientist",
    "specialist",
    "consultant",
    "coordinator",
    "administrator",
    "designer",
    "architect",
    "accountant",
    "auditor",
    "officer",
    "executive",
    "director",
    "supervisor",
    "technician",
    "teacher",
    "lecturer",
    "professor",
    "researcher",
    "nurse",
    "pharmacist",
    "recruiter",
)

TITLE_PATTERN = re.compile(
    r"\b(?:intern|junior|senior|lead|principal|assistant|associate|chief|head)?\s*"
    r"(?:[A-Za-z][A-Za-z&/-]*\s+){0,3}"
    r"(?:" + "|".join(TITLE_SUFFIXES) + r")\b",
    re.IGNORECASE,
)


def _clean_role(value):
    return re.sub(r"\s+", " ", value).strip()


def detect_role_candidates(text):
    """Detect likely job titles explicitly represented in the resume."""

    if not text:
        return []

    candidates = {}

    for match in TITLE_PATTERN.finditer(text):
        role = _clean_role(match.group(0))
        if not role:
            continue
        candidates[role.casefold()] = role

    doc = process_text(text)

    if doc is not None:
        for chunk in doc.noun_chunks:
            phrase = _clean_role(chunk.text)
            lowered = phrase.casefold()

            if any(lowered.endswith(suffix) for suffix in TITLE_SUFFIXES):
                candidates[lowered] = phrase

    return sorted(candidates.values(), key=str.casefold)

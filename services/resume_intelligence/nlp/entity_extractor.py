from collections import defaultdict

from services.resume_intelligence.nlp.nlp_service import process_text

ALLOWED_ENTITY_TYPES = {"PERSON", "ORG", "GPE", "LOC", "DATE", "LANGUAGE"}


def _unique(values):
    """Case-insensitive ordered deduplication."""

    seen = set()
    result = []

    for value in values:
        cleaned = value.strip()

        if not cleaned:
            continue

        key = cleaned.casefold()

        if key in seen:
            continue

        seen.add(key)
        result.append(cleaned)

    return result


def extract_entities(text):
    """Extract useful resume entities."""

    doc = process_text(text)

    if doc is None:
        return {}

    grouped = defaultdict(list)

    for entity in doc.ents:
        if entity.label_ not in ALLOWED_ENTITY_TYPES:
            continue

        value = entity.text.strip()

        if not value:
            continue

        grouped[entity.label_].append(value)

    return {label: _unique(values) for label, values in grouped.items()}


class EntityExtractor:
    """Backward-compatible wrapper class."""

    def extract(self, text):
        return extract_entities(text)

"""Resume intelligence service package."""

from services.resume_intelligence.nlp.entity_extractor import extract_entities
from services.resume_intelligence.nlp.nlp_service import normalize_text
from services.resume_intelligence.nlp.role_detector import detect_role_candidates
from services.resume_intelligence.nlp.skill_extractor import extract_skill_candidates


def analyze_resume_text(text):
    """Run the core NLP resume analysis pipeline."""

    normalized_text = normalize_text(text)

    if not normalized_text:
        return {
            "entities": {},
            "skill_candidates": [],
            "role_candidates": [],
            "word_count": 0,
        }

    return {
        "entities": extract_entities(normalized_text),
        "skill_candidates": extract_skill_candidates(normalized_text),
        "role_candidates": detect_role_candidates(normalized_text),
        "word_count": len(normalized_text.split()),
    }

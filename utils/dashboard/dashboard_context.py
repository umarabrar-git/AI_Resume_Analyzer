from utils.parsing.parser import get_skill_icon, score_tier


def _coerce_mapping(value):
    if hasattr(value, "to_dict"):
        value = value.to_dict()
    elif hasattr(value, "__dict__"):
        value = dict(value.__dict__)

    return value if isinstance(value, dict) else {}


def extract_analysis_session_data(payload, *, resume_text="", job_description=""):
    """Convert workflow output into the flattened session fields used by the templates."""
    payload = _coerce_mapping(payload)

    if isinstance(payload.get("analysis_result"), dict):
        payload = payload["analysis_result"]

    ats = payload.get("ats") or payload.get("ats_result") or payload.get("ats_analysis") or {}
    match = payload.get("job_match") or payload.get("match") or payload.get("match_result") or {}
    resume = payload.get("resume") or payload.get("resume_analysis") or payload.get("nlp") or payload.get("resume_data") or {}
    raw = payload.get("raw") or {}

    skills = resume.get("skills") or resume.get("detected_skills") or resume.get("extracted_skills") or raw.get("skills") or []
    matched_skills = match.get("matched_skills") or match.get("matched_required") or match.get("matched") or raw.get("matched_skills") or []
    missing_skills = match.get("missing_skills") or match.get("missing_required") or match.get("missing") or raw.get("missing_skills") or []

    ats_score = (
        ats.get("ats_score")
        or ats.get("overall_score")
        or ats.get("score")
        or raw.get("ats_score")
        or 0
    )
    match_percentage = (
        match.get("match_percentage")
        or match.get("score")
        or raw.get("match_percentage")
        or 0
    )

    return {
        "name": resume.get("name") or payload.get("name") or raw.get("name") or "Guest",
        "email": resume.get("email") or payload.get("email") or raw.get("email") or "",
        "phone": resume.get("phone") or payload.get("phone") or raw.get("phone") or "",
        "skills": skills,
        "ats_score": int(ats_score) if isinstance(ats_score, (int, float)) else 0,
        "ats_breakdown": {
            "formatting": ats.get("formatting") or ats.get("format_score") or 0,
            "keywords": ats.get("keywords") or ats.get("keyword_score") or 0,
            "sections": ats.get("sections") or ats.get("section_score") or 0,
            "readability": ats.get("readability") or ats.get("readability_score") or 0,
            "content": ats.get("content") or ats.get("content_score") or 0,
        },
        "word_count": ats.get("word_count") or payload.get("word_count") or raw.get("word_count") or 0,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "match_percentage": int(match_percentage) if isinstance(match_percentage, (int, float)) else 0,
        "text": resume_text,
        "job_description": job_description,
        "sections_found": ats.get("sections_found") or resume.get("sections_found") or raw.get("sections_found") or [],
        "page_count": resume.get("page_count") or payload.get("page_count") or raw.get("page_count") or 1,
        "reading_time": resume.get("reading_time") or payload.get("reading_time") or raw.get("reading_time") or 1,
        "resume_status": ats.get("resume_status") or resume.get("resume_status") or payload.get("resume_status") or raw.get("resume_status") or "Needs Improvement",
        "profession_field": resume.get("profession_field") or payload.get("profession_field") or raw.get("profession_field") or "General Professional",
        "profile_strength": resume.get("profile_strength") or payload.get("profile_strength") or raw.get("profile_strength") or 0,
        "profile_checklist": resume.get("profile_checklist") or payload.get("profile_checklist") or raw.get("profile_checklist") or [],
        "format_checks": resume.get("format_checks") or payload.get("format_checks") or raw.get("format_checks") or [],
        "format_score": resume.get("format_score") or payload.get("format_score") or raw.get("format_score") or 0,
        "skill_labels": [skill for skill in skills[:5]] if isinstance(skills, list) else [],
        "skill_scores": [100 if skill in matched_skills else 0 for skill in skills[:5]] if isinstance(skills, list) else [],
    }


def apply_analysis_to_session(session_obj, payload, *, resume_text="", job_description=""):
    """Populate Flask session with flattened fields from analysis results."""
    data = extract_analysis_session_data(payload, resume_text=resume_text, job_description=job_description)
    for key, value in data.items():
        session_obj[key] = value
    session_obj.modified = True
    return data


def build_session_context(session_obj):
    """Return template context from stored session data, or safe defaults."""
    return dict(
        name=session_obj.get("name", "Guest"),
        email=session_obj.get("email", ""),
        phone=session_obj.get("phone", ""),
        skills=session_obj.get("skills", []),
        ats_score=session_obj.get("ats_score", 0),
        ats_breakdown=session_obj.get("ats_breakdown", {}),
        word_count=session_obj.get("word_count", 0),
        matched_skills=session_obj.get("matched_skills", []),
        missing_skills=session_obj.get("missing_skills", []),
        match_percentage=session_obj.get("match_percentage", 0),
        text=session_obj.get("text", ""),
        job_description=session_obj.get("job_description", ""),
        sections_found=session_obj.get("sections_found", []),
        page_count=session_obj.get("page_count", 1),
        reading_time=session_obj.get("reading_time", 1),
        resume_status=session_obj.get("resume_status", "No resume analyzed yet"),
        profession_field=session_obj.get("profession_field", "General Professional"),
        profile_strength=session_obj.get("profile_strength", 0),
        profile_checklist=session_obj.get("profile_checklist", []),
        format_checks=session_obj.get("format_checks", []),
        format_score=session_obj.get("format_score", 0),
        skill_labels=session_obj.get("skill_labels", []),
        skill_scores=session_obj.get("skill_scores", []),
        get_skill_icon=get_skill_icon,
        score_tier=score_tier,
    )

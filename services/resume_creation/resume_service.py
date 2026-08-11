"""Business logic for the AI Resume Builder feature.

Keeps route handlers thin: all validation, sanitization, and ownership
checks for resume drafts live here.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from database import db
from models.resume import Resume
from models.resume_version import ResumeVersion

ALLOWED_TEMPLATES = {"classic", "modern", "professional", "minimal", "technical"}
DEFAULT_TEMPLATE = "classic"

MAX_TITLE_LENGTH = 150
MAX_TEXT_FIELD_LENGTH = 4000
MAX_SHORT_FIELD_LENGTH = 200
MAX_LIST_ENTRIES = 25
MAX_SKILLS = 60
MAX_CUSTOM_SECTIONS = 10
MAX_CUSTOM_ITEMS = 30

DEFAULT_SECTION_ORDER = [
    "personal_information",
    "summary",
    "experience",
    "education",
    "skills",
    "projects",
    "certifications",
    "languages",
]

SECTION_KEYS = set(DEFAULT_SECTION_ORDER) | {"custom_sections"}

PERSONAL_INFO_FIELDS = [
    "full_name", "professional_title", "email", "phone",
    "location", "linkedin", "github", "portfolio",
]

LANGUAGE_PROFICIENCY_VALUES = {
    "basic", "conversational", "professional", "fluent", "native"
}


def empty_content() -> Dict[str, Any]:
    """Return a blank resume content structure."""
    return {
        "personal_information": {field: "" for field in PERSONAL_INFO_FIELDS},
        "summary": "",
        "experience": [],
        "education": [],
        "skills": [],
        "projects": [],
        "certifications": [],
        "languages": [],
        "custom_sections": [],
        "section_order": list(DEFAULT_SECTION_ORDER),
    }


def _clamp_text(value: Any, max_length: int) -> str:
    if value is None:
        return ""
    return str(value).strip()[:max_length]


def _safe_url(value: Any) -> str:
    text = _clamp_text(value, 500)
    if not text:
        return ""
    parsed = urlparse(text)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""
    return text


def _sanitize_personal_information(raw: Any) -> Dict[str, str]:
    raw = raw if isinstance(raw, dict) else {}
    return {
        field: _clamp_text(raw.get(field), MAX_SHORT_FIELD_LENGTH)
        for field in PERSONAL_INFO_FIELDS
    }


def _sanitize_experience_entry(raw: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(raw, dict):
        return None

    bullets = raw.get("bullets")
    if isinstance(bullets, str):
        bullets = [line.strip() for line in bullets.splitlines() if line.strip()]
    if isinstance(bullets, list):
        bullets = [
            _clamp_text(bullet, MAX_TEXT_FIELD_LENGTH)
            for bullet in bullets if str(bullet).strip()
        ][:20]
    else:
        bullets = []

    return {
        "title": _clamp_text(raw.get("title"), MAX_SHORT_FIELD_LENGTH),
        "company": _clamp_text(raw.get("company"), MAX_SHORT_FIELD_LENGTH),
        "location": _clamp_text(raw.get("location"), MAX_SHORT_FIELD_LENGTH),
        "start_date": _clamp_text(raw.get("start_date"), 40),
        "end_date": _clamp_text(raw.get("end_date"), 40),
        "current": bool(raw.get("current")),
        "bullets": bullets,
    }


def _sanitize_education_entry(raw: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(raw, dict):
        return None

    return {
        "degree": _clamp_text(raw.get("degree"), MAX_SHORT_FIELD_LENGTH),
        "field_of_study": _clamp_text(raw.get("field_of_study"), MAX_SHORT_FIELD_LENGTH),
        "institution": _clamp_text(raw.get("institution"), MAX_SHORT_FIELD_LENGTH),
        "location": _clamp_text(raw.get("location"), MAX_SHORT_FIELD_LENGTH),
        "start_date": _clamp_text(raw.get("start_date"), 40),
        "end_date": _clamp_text(raw.get("end_date"), 40),
        "grade": _clamp_text(raw.get("grade"), 40),
        "description": _clamp_text(raw.get("description"), MAX_TEXT_FIELD_LENGTH),
    }


def _sanitize_project_entry(raw: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(raw, dict):
        return None

    technologies = raw.get("technologies")
    if isinstance(technologies, str):
        technologies = [
            token.strip() for token in technologies.split(",") if token.strip()
        ]
    if isinstance(technologies, list):
        technologies = [
            _clamp_text(skill, 60) for skill in technologies if str(skill).strip()
        ][:MAX_SKILLS]
    else:
        technologies = []

    return {
        "name": _clamp_text(raw.get("name"), MAX_SHORT_FIELD_LENGTH),
        "role": _clamp_text(raw.get("role"), MAX_SHORT_FIELD_LENGTH),
        "description": _clamp_text(raw.get("description"), MAX_TEXT_FIELD_LENGTH),
        "technologies": technologies,
        "project_url": _safe_url(raw.get("project_url")),
        "github_url": _safe_url(raw.get("github_url")),
        "start_date": _clamp_text(raw.get("start_date"), 40),
        "end_date": _clamp_text(raw.get("end_date"), 40),
    }


def _sanitize_certification_entry(raw: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(raw, dict):
        return None

    return {
        "name": _clamp_text(raw.get("name"), MAX_SHORT_FIELD_LENGTH),
        "issuer": _clamp_text(raw.get("issuer"), MAX_SHORT_FIELD_LENGTH),
        "issue_date": _clamp_text(raw.get("issue_date"), 40),
        "expiration_date": _clamp_text(raw.get("expiration_date"), 40),
        "credential_id": _clamp_text(raw.get("credential_id"), 100),
        "credential_url": _safe_url(raw.get("credential_url")),
    }


def _sanitize_language_entry(raw: Any) -> Optional[Dict[str, Any]]:
    if isinstance(raw, str):
        language = _clamp_text(raw, 60)
        return {
            "language": language,
            "proficiency": "",
        } if language else None

    if not isinstance(raw, dict):
        return None

    language = _clamp_text(raw.get("language"), 60)
    proficiency = _clamp_text(raw.get("proficiency"), 40).lower()
    if proficiency and proficiency not in LANGUAGE_PROFICIENCY_VALUES:
        proficiency = ""

    if not language:
        return None

    return {
        "language": language,
        "proficiency": proficiency,
    }


def _sanitize_custom_section(raw: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(raw, dict):
        return None

    section_id = _clamp_text(raw.get("id"), 50)
    title = _clamp_text(raw.get("title"), MAX_SHORT_FIELD_LENGTH)

    items_raw = raw.get("items")
    items: List[Dict[str, Any]] = []
    if isinstance(items_raw, list):
        for item in items_raw[:MAX_CUSTOM_ITEMS]:
            if not isinstance(item, dict):
                continue
            bullets = item.get("bullets")
            if isinstance(bullets, str):
                bullets = [line.strip() for line in bullets.splitlines() if line.strip()]
            if isinstance(bullets, list):
                clean_bullets = [
                    _clamp_text(bullet, MAX_TEXT_FIELD_LENGTH)
                    for bullet in bullets if str(bullet).strip()
                ][:20]
            else:
                clean_bullets = []

            items.append({
                "title": _clamp_text(item.get("title"), MAX_SHORT_FIELD_LENGTH),
                "subtitle": _clamp_text(item.get("subtitle"), MAX_SHORT_FIELD_LENGTH),
                "date": _clamp_text(item.get("date"), 60),
                "description": _clamp_text(item.get("description"), MAX_TEXT_FIELD_LENGTH),
                "bullets": clean_bullets,
            })

    if not title:
        return None

    normalized_id = section_id or title.casefold().replace(" ", "-")[:50]
    return {
        "id": normalized_id,
        "title": title,
        "items": items,
    }


def _normalize_section_order(raw_order: Any, custom_sections: List[Dict[str, Any]]) -> List[str]:
    base = list(DEFAULT_SECTION_ORDER)
    custom_keys = [f"custom:{section['id']}" for section in custom_sections if section.get("id")]

    if not isinstance(raw_order, list):
        return base + custom_keys

    allowed = set(base) | set(custom_keys)
    ordered = [key for key in raw_order if key in allowed]

    for key in base + custom_keys:
        if key not in ordered:
            ordered.append(key)

    return ordered


def sanitize_content(raw: Any) -> Dict[str, Any]:
    """Validate/normalize an incoming resume content payload. Never trust client input directly."""
    raw = raw if isinstance(raw, dict) else {}
    content = empty_content()

    content["personal_information"] = _sanitize_personal_information(raw.get("personal_information"))
    content["summary"] = _clamp_text(raw.get("summary"), MAX_TEXT_FIELD_LENGTH)

    experience = raw.get("experience")
    if isinstance(experience, list):
        content["experience"] = [
            entry for entry in (
                _sanitize_experience_entry(item) for item in experience[:MAX_LIST_ENTRIES]
            ) if entry
        ]

    education = raw.get("education")
    if isinstance(education, list):
        content["education"] = [
            entry for entry in (
                _sanitize_education_entry(item) for item in education[:MAX_LIST_ENTRIES]
            ) if entry
        ]

    skills = raw.get("skills")
    if isinstance(skills, list):
        seen = set()
        clean_skills: List[str] = []
        for skill in skills[:MAX_SKILLS]:
            name = _clamp_text(skill, 60)
            key = name.casefold()
            if name and key not in seen:
                seen.add(key)
                clean_skills.append(name)
        content["skills"] = clean_skills

    projects = raw.get("projects")
    if isinstance(projects, list):
        content["projects"] = [
            entry for entry in (
                _sanitize_project_entry(item) for item in projects[:MAX_LIST_ENTRIES]
            ) if entry
        ]

    certifications = raw.get("certifications")
    if isinstance(certifications, list):
        content["certifications"] = [
            entry for entry in (
                _sanitize_certification_entry(item) for item in certifications[:MAX_LIST_ENTRIES]
            ) if entry
        ]

    languages = raw.get("languages")
    if isinstance(languages, list):
        content["languages"] = [
            entry for entry in (
                _sanitize_language_entry(item) for item in languages[:MAX_LIST_ENTRIES]
            ) if entry
        ]

    custom_sections = raw.get("custom_sections")
    if isinstance(custom_sections, list):
        content["custom_sections"] = [
            section for section in (
                _sanitize_custom_section(item) for item in custom_sections[:MAX_CUSTOM_SECTIONS]
            ) if section
        ]

    section_order = raw.get("section_order")
    content["section_order"] = _normalize_section_order(
        section_order,
        content["custom_sections"],
    )

    return content


def compute_completeness(content: Dict[str, Any]) -> int:
    """Deterministic completeness score (0-100) based on which sections have real data."""
    personal = content.get("personal_information") or {}

    checks = [
        bool(personal.get("full_name")),
        bool(personal.get("email")),
        bool(personal.get("phone")),
        bool(content.get("summary")),
        bool(content.get("experience")),
        bool(content.get("education")),
        bool(content.get("skills")),
        bool(content.get("projects")),
    ]

    return round(sum(1 for check in checks if check) / len(checks) * 100)


def list_resumes_for_user(user_id: int) -> List[Resume]:
    return (
        Resume.query
        .filter_by(user_id=user_id)
        .order_by(Resume.updated_at.desc())
        .all()
    )


def get_owned_resume(resume_id: int, user_id: int) -> Optional[Resume]:
    """Fetch a resume only if it belongs to the given user. Never trust resume_id alone."""
    resume = db.session.get(Resume, resume_id)
    if resume is None or resume.user_id != user_id:
        return None
    return resume


def create_resume(
    user_id: int,
    *,
    title: str = "",
    target_role: str = "",
    from_content: Optional[Dict[str, Any]] = None,
) -> Resume:
    resume = Resume(
        user_id=user_id,
        title=_clamp_text(title, MAX_TITLE_LENGTH) or "Untitled Resume",
        target_role=_clamp_text(target_role, MAX_SHORT_FIELD_LENGTH) or None,
        template=DEFAULT_TEMPLATE,
    )
    resume.set_content(sanitize_content(from_content or empty_content()))
    db.session.add(resume)
    db.session.commit()
    return resume


def update_resume(
    resume: Resume,
    *,
    title: Optional[str] = None,
    target_role: Optional[str] = None,
    template: Optional[str] = None,
    content: Optional[Dict[str, Any]] = None,
) -> Resume:
    if title is not None:
        clean_title = _clamp_text(title, MAX_TITLE_LENGTH)
        if clean_title:
            resume.title = clean_title

    if target_role is not None:
        resume.target_role = _clamp_text(target_role, MAX_SHORT_FIELD_LENGTH) or None

    if template is not None and template in ALLOWED_TEMPLATES:
        resume.template = template

    if content is not None:
        resume.set_content(sanitize_content(content))

    db.session.commit()
    return resume


def duplicate_resume(resume: Resume) -> Resume:
    clone = Resume(
        user_id=resume.user_id,
        title=_clamp_text(f"{resume.title} (Copy)", MAX_TITLE_LENGTH),
        target_role=resume.target_role,
        template=resume.template,
        content_json=resume.content_json,
    )
    db.session.add(clone)
    db.session.commit()
    return clone


def delete_resume(resume: Resume) -> None:
    db.session.delete(resume)
    db.session.commit()


def create_resume_version(
    resume: Resume,
    *,
    action: str = "manual_save",
    note: Optional[str] = None,
) -> ResumeVersion:
    version = ResumeVersion(
        resume_id=resume.id,
        user_id=resume.user_id,
        action=_clamp_text(action, 50) or "manual_save",
        note=_clamp_text(note, 255) or None,
        title=resume.title,
        target_role=resume.target_role,
        template=resume.template,
        content_json=resume.content_json,
    )
    db.session.add(version)
    db.session.commit()
    return version


def list_versions_for_resume(resume_id: int, user_id: int) -> List[ResumeVersion]:
    return (
        ResumeVersion.query
        .filter_by(resume_id=resume_id, user_id=user_id)
        .order_by(ResumeVersion.created_at.desc())
        .all()
    )


def get_owned_resume_version(version_id: int, user_id: int) -> Optional[ResumeVersion]:
    version = db.session.get(ResumeVersion, version_id)
    if version is None or version.user_id != user_id:
        return None
    return version


def restore_resume_from_version(resume: Resume, version: ResumeVersion) -> Resume:
    resume.title = version.title
    resume.target_role = version.target_role
    resume.template = version.template
    resume.content_json = version.content_json
    db.session.commit()
    return resume


def build_content_from_analysis(session_obj) -> Dict[str, Any]:
    """Seed resume content from a previously analyzed resume in the session.

    Only pulls values the user actually has (from real analysis output);
    never invents experience, education, or skills.
    """
    content = empty_content()

    content["personal_information"]["full_name"] = _clamp_text(
        session_obj.get("name"), MAX_SHORT_FIELD_LENGTH
    )
    content["personal_information"]["email"] = _clamp_text(
        session_obj.get("email"), MAX_SHORT_FIELD_LENGTH
    )
    content["personal_information"]["phone"] = _clamp_text(
        session_obj.get("phone"), MAX_SHORT_FIELD_LENGTH
    )

    skills = session_obj.get("skills") or []
    if isinstance(skills, list):
        content["skills"] = [
            _clamp_text(skill, 60) for skill in skills[:MAX_SKILLS] if str(skill).strip()
        ]

    profession_field = _clamp_text(session_obj.get("profession_field"), MAX_SHORT_FIELD_LENGTH)
    if profession_field:
        content["personal_information"]["professional_title"] = profession_field

    return content

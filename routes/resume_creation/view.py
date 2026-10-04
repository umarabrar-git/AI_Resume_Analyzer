from __future__ import annotations

import io
import os
import secrets
import tempfile
from typing import Any, Dict, List, Optional

from flask import current_app, jsonify, render_template, request, session, send_file
from docx import Document
from docx.shared import RGBColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from database import db
from models.user import User

from routes.auth import login_required
from utils import build_session_context
from services.resume_creation.resume_service import (
    ALLOWED_TEMPLATES,
    DEFAULT_TEMPLATE,
    build_content_from_analysis,
    compute_completeness,
    create_resume,
    create_resume_version,
    delete_resume,
    duplicate_resume,
    get_owned_resume,
    get_owned_resume_version,
    list_versions_for_resume,
    list_resumes_for_user,
    restore_resume_from_version,
    sanitize_content,
    update_resume,
)
from services.resume_creation.template_registry import (
    TEMPLATE_REGISTRY,
    can_use_template,
    get_template_catalog,
)
from services.resume_intelligence.ats import analyze_ats
from services.resume_intelligence.generative.local_generation import (
    TASK_BULLETS,
    TASK_EXPERIENCE,
    TASK_RESUME_REWRITE,
    TASK_SUMMARY,
    local_generate,
)
from services.resume_intelligence.generative.validators import validate_generated_claims
from services.resume_intelligence.matching.job_matcher import match_resume_to_job
from services.resume_intelligence.agents import get_agent_service, initialize_agent_service
from utils import allowed_file, extract_resume_text
from utils.parsing.parser import (
    RESUME_SECTION_HEADERS,
    SECTION_ICON_MAP,
    extract_email,
    extract_name,
    extract_phone,
    extract_skills,
)


@login_required
def render_resume_creation():
    csrf_token = session.get("resume_csrf_token")
    if not csrf_token:
        csrf_token = secrets.token_urlsafe(32)
        session["resume_csrf_token"] = csrf_token
    context = build_session_context(session)
    context["resume_csrf_token"] = csrf_token
    return render_template("resume_creation.html", **context)


def _api_error(status: int, message: str, *, code: str = "error"):
    return jsonify({"success": False, "error": message, "code": code}), status


def _require_api_user_id() -> Optional[int]:
    raw_user_id = session.get("user_id")
    if raw_user_id is None:
        return None
    try:
        return int(raw_user_id)
    except (TypeError, ValueError):
        return None


def _user_subscription_plan(user_id: int) -> str:
    user = db.session.get(User, user_id)
    return str(user.subscription_plan or "free").strip().lower() if user else "free"


def _template_access_error(template_id: str, user_id: int):
    if template_id not in ALLOWED_TEMPLATES:
        return _api_error(422, "Invalid template.", code="invalid_template")
    if not can_use_template(template_id, _user_subscription_plan(user_id)):
        return _api_error(403, "This template requires a Pro or Enterprise plan.", code="premium_required")
    return None


def _resume_payload(resume, subscription_plan: Optional[str] = None) -> Dict[str, Any]:
    payload = resume.to_dict()
    payload["completeness"] = compute_completeness(payload.get("content") or {})
    plan = subscription_plan or _user_subscription_plan(resume.user_id)
    if not can_use_template(payload.get("template"), plan):
        payload["locked_template"] = payload["template"]
        payload["template"] = DEFAULT_TEMPLATE
    return payload


def _filename_safe(value: str) -> str:
    safe = "".join(char for char in str(value or "resume") if char.isalnum() or char in {"-", "_", " "}).strip()
    safe = "-".join(safe.split())
    return safe[:80] or "resume"


def _content_to_text(content: Dict[str, Any]) -> str:
    lines: List[str] = []
    for section in _content_to_sections(content):
        if section.get("title"):
            lines.append(str(section["title"]))
        lines.extend(str(line) for line in section.get("lines") or [] if str(line).strip())
        lines.extend(str(bullet) for bullet in section.get("bullets") or [] if str(bullet).strip())

    return "\n".join(lines).strip()


def _content_to_sections(content: Dict[str, Any]) -> List[Dict[str, Any]]:
    personal = content.get("personal_information") or {}
    contact = [
        str(personal.get(key) or "").strip()
        for key in ("email", "phone", "location")
    ]
    links = [
        str(personal.get(key) or "").strip()
        for key in ("linkedin", "github", "portfolio")
    ]
    header_lines = [
        str(personal.get("full_name") or "").strip(),
        str(personal.get("professional_title") or "").strip(),
        " | ".join(value for value in contact if value),
        " | ".join(value for value in links if value),
    ]
    rendered = [{
        "key": "personal_information",
        "title": "",
        "lines": [line for line in header_lines if line],
        "bullets": [],
    }]

    def simple_section(key: str, title: str, value: Any) -> Optional[Dict[str, Any]]:
        text = str(value or "").strip()
        return {"key": key, "title": title, "lines": [text], "bullets": []} if text else None

    def rows_section(key: str, title: str, rows: Any, line_builder, bullet_builder=None):
        if not isinstance(rows, list) or not rows:
            return None
        lines: List[str] = []
        bullets: List[str] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            lines.extend(line_builder(row))
            if bullet_builder:
                bullets.extend(bullet_builder(row))
        if not lines and not bullets:
            return None
        return {"key": key, "title": title, "lines": lines, "bullets": bullets}

    section_builders = {
        "summary": lambda: simple_section("summary", "Summary", content.get("summary")),
        "career_objective": lambda: simple_section("career_objective", "Career Objective", content.get("career_objective")),
        "experience": lambda: rows_section(
            "experience", "Experience", content.get("experience"),
            lambda row: [" | ".join(value for value in (
                str(row.get("title") or "").strip(),
                str(row.get("company") or "").strip(),
                str(row.get("location") or "").strip(),
                str(row.get("start_date") or "").strip(),
                "Present" if row.get("current") else str(row.get("end_date") or "").strip(),
            ) if value)],
            lambda row: [str(value).strip() for value in (row.get("bullets") or []) + (row.get("achievements") or []) if str(value).strip()],
        ),
        "education": lambda: rows_section(
            "education", "Education", content.get("education"),
            lambda row: [" | ".join(value for value in (
                str(row.get("degree") or "").strip(),
                str(row.get("field_of_study") or "").strip(),
                str(row.get("institution") or "").strip(),
                str(row.get("location") or "").strip(),
                str(row.get("start_date") or "").strip(),
                str(row.get("end_date") or "").strip(),
                str(row.get("grade") or "").strip(),
            ) if value)],
            lambda row: [str(value).strip() for value in (
                [row.get("description"), row.get("coursework"), row.get("academic_achievements")]
            ) if value and str(value).strip()],
        ),
        "skills": lambda: rows_section(
            "skills", "Skills", [content.get("skills_by_category") or {}],
            lambda row: [f"{category}: {', '.join(str(skill) for skill in skills)}" for category, skills in row.items() if skills],
        ) or simple_section("skills", "Skills", ", ".join(content.get("skills") or [])),
        "projects": lambda: rows_section(
            "projects", "Projects", content.get("projects"),
            lambda row: [" | ".join(value for value in (
                str(row.get("name") or "").strip(),
                str(row.get("role") or "").strip(),
                ", ".join(str(item) for item in (row.get("technologies") or [])),
                str(row.get("project_url") or "").strip(),
                str(row.get("github_url") or "").strip(),
            ) if value)],
            lambda row: [str(value).strip() for value in [row.get("description"), *(row.get("achievements") or [])] if value and str(value).strip()],
        ),
        "certifications": lambda: rows_section(
            "certifications", "Certifications", content.get("certifications"),
            lambda row: [" | ".join(value for value in (
                str(row.get("name") or "").strip(),
                str(row.get("issuer") or "").strip(),
                str(row.get("issue_date") or "").strip(),
                str(row.get("credential_id") or "").strip(),
                str(row.get("credential_url") or "").strip(),
            ) if value)],
        ),
        "languages": lambda: rows_section(
            "languages", "Languages", content.get("languages"),
            lambda row: [" ".join(value for value in (
                str(row.get("language") or "").strip(),
                str(row.get("proficiency") or "").strip(),
            ) if value)],
        ),
    }

    custom_by_key = {
        f"custom:{section.get('id')}": section
        for section in content.get("custom_sections") or []
        if isinstance(section, dict) and section.get("id")
    }
    hidden = set(content.get("hidden_sections") or [])
    for key in content.get("section_order") or []:
        if key == "personal_information" or key in hidden:
            continue
        if key in section_builders:
            section = section_builders[key]()
        else:
            custom = custom_by_key.get(key)
            if not custom:
                continue
            lines: List[str] = []
            bullets: List[str] = []
            for item in custom.get("items") or []:
                if not isinstance(item, dict):
                    continue
                descriptor = " | ".join(value for value in (
                    str(item.get("title") or "").strip(),
                    str(item.get("subtitle") or "").strip(),
                    str(item.get("date") or "").strip(),
                ) if value)
                if descriptor:
                    lines.append(descriptor)
                if item.get("description"):
                    lines.append(str(item["description"]).strip())
                bullets.extend(str(value).strip() for value in item.get("bullets") or [] if str(value).strip())
            section = {"key": key, "title": str(custom.get("title") or "Custom Section"), "lines": lines, "bullets": bullets}
            if not lines and not bullets:
                section = None
        if section:
            rendered.append(section)
    return rendered


def _export_pdf_bytes(resume) -> bytes:
    content = sanitize_content(resume.get_content())
    sections = _content_to_sections(content)
    theme = TEMPLATE_REGISTRY.get(resume.template, TEMPLATE_REGISTRY[DEFAULT_TEMPLATE])
    accent = HexColor(theme["accent"])
    font_name = theme["font"]
    bold_font = {"Helvetica": "Helvetica-Bold", "Times-Roman": "Times-Bold", "Courier": "Courier-Bold"}[font_name]

    buffer = io.BytesIO()
    doc = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 0.75 * inch
    left = 0.75 * inch
    line_height = 14

    def ensure_space(lines_needed: int = 1):
        nonlocal y
        if y - (lines_needed * line_height) < 0.75 * inch:
            doc.showPage()
            y = height - 0.75 * inch

    for idx, section in enumerate(sections):
        title = section.get("title") or ""
        lines = section.get("lines") or []
        bullets = section.get("bullets") or []

        if idx == 0:
            for i, line in enumerate(lines):
                if not line:
                    continue
                ensure_space()
                if i == 0:
                    doc.setFillColor(accent)
                    doc.setFont(bold_font, 15)
                elif i == 1:
                    doc.setFillColor(accent)
                    doc.setFont(font_name, 11)
                else:
                    doc.setFillColorRGB(0.16, 0.20, 0.25)
                    doc.setFont(font_name, 9.5)
                doc.drawString(left, y, line[:125])
                y -= line_height
            y -= 8
            continue

        if title:
            ensure_space(2)
            doc.setFillColor(accent)
            doc.setFont(bold_font, 11)
            doc.drawString(left, y, title.upper()[:90])
            y -= line_height
            doc.setLineWidth(0.5)
            doc.line(left, y + 4, width - left, y + 4)

        doc.setFillColorRGB(0.16, 0.20, 0.25)
        doc.setFont(font_name, 9.7)
        for line in lines:
            if not line:
                continue
            ensure_space()
            doc.drawString(left, y, line[:130])
            y -= line_height

        for bullet in bullets:
            if not bullet:
                continue
            ensure_space()
            doc.drawString(left + 8, y, f"- {bullet}"[:128])
            y -= line_height

        y -= 6

    doc.save()
    buffer.seek(0)
    return buffer.getvalue()


def _export_docx_bytes(resume) -> bytes:
    content = sanitize_content(resume.get_content())
    sections = _content_to_sections(content)

    document = Document()
    theme = TEMPLATE_REGISTRY.get(resume.template, TEMPLATE_REGISTRY[DEFAULT_TEMPLATE])
    accent = theme["accent"].lstrip("#")
    normal_style = document.styles["Normal"]
    normal_style.font.name = theme["font"]
    for style_name in ("Heading 1", "Heading 2"):
        heading_style = document.styles[style_name]
        heading_style.font.name = theme["font"]
        heading_style.font.color.rgb = RGBColor.from_string(accent)

    for idx, section in enumerate(sections):
        title = section.get("title") or ""
        lines = section.get("lines") or []
        bullets = section.get("bullets") or []

        if idx == 0:
            if lines:
                heading = document.add_paragraph(lines[0])
                if heading.runs:
                    heading.runs[0].bold = True
                    heading.runs[0].font.size = None
            for line in lines[1:]:
                if line:
                    document.add_paragraph(line)
            continue

        if title:
            document.add_heading(title, level=2)
        for line in lines:
            if line:
                document.add_paragraph(line)
        for bullet in bullets:
            if bullet:
                document.add_paragraph(bullet, style="List Bullet")

    output = io.BytesIO()
    document.save(output)
    output.seek(0)
    return output.getvalue()


def _get_resume_source_for_generation(content: Dict[str, Any], body: Dict[str, Any]) -> str:
    source_text = str(body.get("source_text") or "").strip()
    if source_text:
        return source_text

    source_type = str(body.get("source_type") or "").strip().lower()
    source_index = body.get("source_index")

    if source_type == "experience" and isinstance(source_index, int):
        rows = content.get("experience") or []
        if 0 <= source_index < len(rows) and isinstance(rows[source_index], dict):
            row = rows[source_index]
            bullets = row.get("bullets") or []
            return "\n".join(str(line).strip() for line in bullets if str(line).strip())

    if source_type == "project" and isinstance(source_index, int):
        rows = content.get("projects") or []
        if 0 <= source_index < len(rows) and isinstance(rows[source_index], dict):
            return str(rows[source_index].get("description") or "").strip()

    if source_type == "summary":
        return str(content.get("summary") or "").strip()

    return ""


def _apply_generated_content(resume, body: Dict[str, Any], generated_text: str):
    apply_to = str(body.get("apply_to") or "").strip().lower()
    source_index = body.get("source_index")

    content = resume.get_content()

    if apply_to == "summary":
        content["summary"] = generated_text.strip()
        update_resume(resume, content=content)
        return

    if apply_to == "career_objective":
        content["career_objective"] = generated_text.strip()
        update_resume(resume, content=content)
        return

    if apply_to == "experience" and isinstance(source_index, int):
        experience = content.get("experience") or []
        if 0 <= source_index < len(experience) and isinstance(experience[source_index], dict):
            bullet_lines = [
                line.strip("•- \t") for line in generated_text.splitlines() if line.strip("•- \t")
            ]
            experience[source_index]["bullets"] = bullet_lines
            content["experience"] = experience
            update_resume(resume, content=content)
            return

    if apply_to == "project" and isinstance(source_index, int):
        projects = content.get("projects") or []
        if 0 <= source_index < len(projects) and isinstance(projects[source_index], dict):
            projects[source_index]["description"] = generated_text.strip()
            content["projects"] = projects
            update_resume(resume, content=content)


def _normalize_priority(value: str) -> str:
    level = str(value or "").strip().lower()
    if level in {"high", "critical"}:
        return "high"
    if level in {"medium", "moderate"}:
        return "medium"
    return "low"


def _recommendation_sort_key(item: Dict[str, Any]):
    rank = {"high": 0, "medium": 1, "low": 2}
    return (rank.get(item.get("priority") or "low", 2), str(item.get("title") or ""))


def _build_resume_intelligence(
    content: Dict[str, Any],
    ats: Dict[str, Any],
    match_result: Optional[Dict[str, Any]],
    job_description: str,
) -> Dict[str, Any]:
    personal = content.get("personal_information") or {}
    experience = content.get("experience") or []
    projects = content.get("projects") or []
    skills = content.get("skills") or []

    recommendations: List[Dict[str, Any]] = []

    for rec in ats.get("recommendations") or []:
        if not isinstance(rec, dict):
            continue
        recommendations.append({
            "priority": _normalize_priority(rec.get("priority") or "medium"),
            "type": str(rec.get("type") or "general"),
            "title": str(rec.get("title") or "Improve Resume").strip(),
            "detail": str(rec.get("message") or "").strip(),
            "action": "review_section",
        })

    total_bullets = 0
    quantified_bullets = 0
    for entry in experience:
        if not isinstance(entry, dict):
            continue
        bullets = entry.get("bullets") or []
        for bullet in bullets:
            bullet_text = str(bullet).strip()
            if not bullet_text:
                continue
            total_bullets += 1
            if any(char.isdigit() for char in bullet_text):
                quantified_bullets += 1

    if content.get("summary") and len(str(content.get("summary") or "").split()) < 25:
        recommendations.append({
            "priority": "high",
            "type": "content",
            "title": "Strengthen Professional Summary",
            "detail": "Your summary is short. Add clearer value proposition, domain focus, and impact.",
            "action": "ai_rewrite_summary",
        })

    if experience and total_bullets < max(3, len(experience) * 2):
        recommendations.append({
            "priority": "high",
            "type": "experience",
            "title": "Add More Experience Evidence",
            "detail": "Each role should show impact through multiple bullet points.",
            "action": "add_experience_bullets",
        })

    if total_bullets and quantified_bullets / total_bullets < 0.35:
        recommendations.append({
            "priority": "medium",
            "type": "experience",
            "title": "Increase Quantified Achievements",
            "detail": "Add metrics, scope, or outcomes to bullet points for stronger credibility.",
            "action": "quantify_bullets",
        })

    if not projects:
        recommendations.append({
            "priority": "medium",
            "type": "projects",
            "title": "Add A Project Section",
            "detail": "Projects help demonstrate practical delivery and tool usage.",
            "action": "add_projects",
        })

    if not personal.get("professional_title"):
        recommendations.append({
            "priority": "medium",
            "type": "branding",
            "title": "Set A Professional Title",
            "detail": "Add a clear headline to instantly communicate your role focus.",
            "action": "update_personal_header",
        })

    missing_candidates: List[str] = []
    semantic_score = None
    candidate_match_score = None

    if isinstance(match_result, dict):
        semantic_score = match_result.get("semantic_score")
        candidate_match_score = match_result.get("candidate_match_score")
        missing_candidates = [str(item).strip() for item in (match_result.get("missing_candidates") or []) if str(item).strip()]

        if missing_candidates:
            recommendations.append({
                "priority": "high",
                "type": "keywords",
                "title": "Cover Missing Job Keywords",
                "detail": "Add evidence for top missing skills from the job description.",
                "action": "apply_missing_skills",
            })

        if isinstance(semantic_score, (int, float)) and semantic_score < 70:
            recommendations.append({
                "priority": "high",
                "type": "targeting",
                "title": "Tailor Resume To Job",
                "detail": "Your semantic alignment with this JD is low. Tailor summary and experience to role needs.",
                "action": "ai_tailor_resume",
            })

    seen_titles = set()
    deduped_recommendations = []
    for rec in recommendations:
        title_key = str(rec.get("title") or "").casefold().strip()
        if not title_key or title_key in seen_titles:
            continue
        seen_titles.add(title_key)
        deduped_recommendations.append(rec)

    deduped_recommendations.sort(key=_recommendation_sort_key)

    ats_score = float(ats.get("ats_score") or 0.0)
    readiness_score = ats_score
    if isinstance(semantic_score, (int, float)):
        readiness_score = round((ats_score * 0.65) + (float(semantic_score) * 0.35), 2)

    diagnostics = {
        "section_gaps": [
            section
            for section, present in {
                "summary": bool(content.get("summary")),
                "experience": bool(experience),
                "education": bool(content.get("education") or []),
                "skills": bool(skills),
                "projects": bool(projects),
            }.items()
            if not present
        ],
        "bullet_count": total_bullets,
        "quantified_bullet_count": quantified_bullets,
        "missing_keywords": missing_candidates[:12],
        "analysis_mode": (match_result or {}).get("analysis_mode") if isinstance(match_result, dict) else None,
    }

    return {
        "readiness_score": readiness_score,
        "ats_score": ats_score,
        "semantic_score": semantic_score,
        "candidate_match_score": candidate_match_score,
        "high_priority_count": sum(1 for rec in deduped_recommendations if rec.get("priority") == "high"),
        "recommendations": deduped_recommendations[:10],
        "diagnostics": diagnostics,
        "job_description_used": bool(job_description),
    }


def api_list_resumes():
    user_id = _require_api_user_id()
    if user_id is None:
        return _api_error(401, "Authentication required.", code="auth_required")

    plan = _user_subscription_plan(user_id)
    templates = get_template_catalog(plan)
    resumes = [_resume_payload(resume, plan) for resume in list_resumes_for_user(user_id)]
    return jsonify({
        "success": True,
        "resumes": resumes,
        "templates": templates,
        "allowed_templates": [item["id"] for item in templates if item["available"]],
    })


def api_create_resume():
    user_id = _require_api_user_id()
    if user_id is None:
        return _api_error(401, "Authentication required.", code="auth_required")

    body = request.get_json(silent=True) or {}
    creation_method = str(body.get("creation_method") or "scratch").strip().lower()
    title = body.get("title") or ""
    target_role = body.get("target_role") or ""
    template = body.get("template")
    if template:
        access_error = _template_access_error(template, user_id)
        if access_error:
            return access_error

    try:
        if creation_method == "analysis":
            content = build_content_from_analysis(session)
            resume = create_resume(
                user_id,
                title=title,
                target_role=target_role,
                from_content=content,
            )
        elif creation_method == "profile":
            user = db.session.get(User, user_id)
            if user is None:
                return _api_error(404, "Profile not found.", code="profile_not_found")
            content = {
                "personal_information": {
                    "full_name": user.full_name or "",
                    "email": user.email or "",
                }
            }
            resume = create_resume(
                user_id,
                title=title or "Resume from Profile",
                target_role=target_role,
                from_content=content,
            )
        elif creation_method == "duplicate":
            source_resume_id = body.get("source_resume_id")
            if not isinstance(source_resume_id, int):
                return _api_error(422, "source_resume_id is required for duplication.", code="invalid_payload")
            source_resume = get_owned_resume(source_resume_id, user_id)
            if source_resume is None:
                return _api_error(404, "Source resume not found.", code="not_found")
            resume = duplicate_resume(source_resume)
            plan = _user_subscription_plan(user_id)
            if not can_use_template(resume.template, plan):
                update_resume(resume, template=DEFAULT_TEMPLATE)
        elif creation_method == "ai_assisted":
            seed_content = body.get("content") if isinstance(body.get("content"), dict) else {}
            resume = create_resume(
                user_id,
                title=title or "AI Draft Resume",
                target_role=target_role,
                from_content=seed_content,
            )
        else:
            resume = create_resume(
                user_id,
                title=title,
                target_role=target_role,
                from_content=body.get("content") if isinstance(body.get("content"), dict) else None,
            )

        if template:
            update_resume(resume, template=template)

        return jsonify({
            "success": True,
            "resume": _resume_payload(resume, _user_subscription_plan(user_id)),
        }), 201
    except Exception:
        return _api_error(500, "Unable to create resume.", code="create_failed")


def api_import_resume():
    user_id = _require_api_user_id()
    if user_id is None:
        return _api_error(401, "Authentication required.", code="auth_required")

    uploaded_file = request.files.get("resume")
    filename = str(getattr(uploaded_file, "filename", "") or "")
    allowed_extensions = current_app.config.get("ALLOWED_EXTENSIONS", {"pdf", "docx"})
    if uploaded_file is None or not filename or not allowed_file(filename, allowed_extensions):
        return _api_error(422, "Choose a PDF or DOCX resume to import.", code="invalid_file")

    extension = filename.rsplit(".", 1)[-1].lower()
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, f"resume.{extension}")
            uploaded_file.save(filepath)
            if os.path.getsize(filepath) > 10 * 1024 * 1024:
                return _api_error(413, "Resume file must be 10 MB or smaller.", code="file_too_large")
            text = str(extract_resume_text(filepath, extension) or "").strip()
    except Exception:
        return _api_error(422, "This file could not be read. Try a text-based PDF or DOCX.", code="parse_failed")

    if not text:
        return _api_error(422, "No readable text was found in this resume.", code="empty_resume")

    extracted_name = extract_name(text)
    extracted_email = extract_email(text)
    extracted_phone = extract_phone(text)
    section_labels = {
        **SECTION_ICON_MAP,
        "volunteer experience": "Volunteer Experience",
        "research experience": "Research",
        "professional summary": "Summary",
        "career objective": "Career Objective",
    }
    heading_map = {
        heading.casefold(): section_labels.get(heading.casefold(), heading.title())
        for heading in RESUME_SECTION_HEADERS
    }
    heading_map.update({
        "volunteer experience": "Volunteer Experience",
        "research experience": "Research",
        "career objective": "Career Objective",
    })
    extracted_sections: List[Dict[str, str]] = []
    active_heading = None
    active_lines: List[str] = []
    for line in text.splitlines():
        normalized_heading = line.strip().casefold().rstrip(":-").strip()
        if normalized_heading in heading_map:
            if active_heading and active_lines:
                extracted_sections.append({
                    "title": active_heading,
                    "text": "\n".join(active_lines).strip(),
                })
            active_heading = heading_map[normalized_heading]
            active_lines = []
        elif active_heading and line.strip():
            active_lines.append(line.strip())
    if active_heading and active_lines:
        extracted_sections.append({
            "title": active_heading,
            "text": "\n".join(active_lines).strip(),
        })

    imported_custom_sections = []
    section_order = ["personal_information", "summary", "career_objective"]
    summary_text = ""
    objective_text = ""
    for imported_section in extracted_sections[:8]:
        title = imported_section["title"]
        block_text = imported_section["text"]
        normalized_title = title.casefold()
        if normalized_title in {"summary", "profile"} and not summary_text:
            summary_text = block_text
            continue
        if normalized_title in {"objective", "career objective"} and not objective_text:
            objective_text = block_text
            continue
        if normalized_title == "skills":
            continue
        section_id = f"imported-{len(imported_custom_sections) + 1}"
        imported_custom_sections.append({
            "id": section_id,
            "title": title,
            "items": [{"title": f"Imported {title}", "description": block_text}],
        })
        section_order.append(f"custom:{section_id}")

    imported_custom_sections.append({
        "id": "imported-original-text",
        "title": "Original Imported Resume",
        "items": [{"title": "Extracted source text", "description": text[:4000]}],
    })
    section_order.append("custom:imported-original-text")
    content = {
        "personal_information": {
            "full_name": "" if extracted_name == "Name Not Found" else extracted_name,
            "email": "" if extracted_email == "Email Not Found" else extracted_email,
            "phone": "" if extracted_phone == "Phone Number Not Found" else extracted_phone,
        },
        "summary": summary_text,
        "career_objective": objective_text,
        "skills": extract_skills(text),
        "custom_sections": imported_custom_sections,
        "section_order": section_order + [
            key for key in ("experience", "education", "skills", "projects", "certifications", "languages")
            if key not in section_order
        ],
    }
    resume = create_resume(
        user_id,
        title=os.path.splitext(os.path.basename(filename))[0] or "Imported Resume",
        from_content=content,
    )
    return jsonify({"success": True, "resume": _resume_payload(resume)}), 201


def api_get_resume(resume_id: int):
    user_id = _require_api_user_id()
    if user_id is None:
        return _api_error(401, "Authentication required.", code="auth_required")

    resume = get_owned_resume(resume_id, user_id)
    if resume is None:
        return _api_error(404, "Resume not found.", code="not_found")

    return jsonify({"success": True, "resume": _resume_payload(resume)})


def api_update_resume(resume_id: int):
    user_id = _require_api_user_id()
    if user_id is None:
        return _api_error(401, "Authentication required.", code="auth_required")

    resume = get_owned_resume(resume_id, user_id)
    if resume is None:
        return _api_error(403, "You cannot modify this resume.", code="ownership_violation")

    body = request.get_json(silent=True) or {}
    template = body.get("template")
    content = body.get("content")

    expected_updated_at = str(body.get("base_updated_at") or "").strip()
    current_updated_at = resume.updated_at.isoformat() if resume.updated_at else ""
    if expected_updated_at and current_updated_at and expected_updated_at != current_updated_at:
        return _api_error(409, "This resume changed in another session. Reload before saving.", code="stale_update")

    if template is not None:
        access_error = _template_access_error(template, user_id)
        if access_error:
            return access_error

    if content is not None and not isinstance(content, dict):
        return _api_error(422, "Invalid content payload.", code="invalid_payload")

    has_any_change = any(
        key in body for key in ("title", "target_role", "template", "content")
    )
    if not has_any_change:
        return _api_error(400, "No changes provided.", code="invalid_payload")

    try:
        update_resume(
            resume,
            title=body.get("title") if "title" in body else None,
            target_role=body.get("target_role") if "target_role" in body else None,
            template=template,
            content=content if isinstance(content, dict) else None,
        )

        if not bool(body.get("autosave")):
            create_resume_version(
                resume,
                action="manual_save",
                note="Manual save from builder workspace",
            )

        return jsonify({
            "success": True,
            "resume": _resume_payload(resume, _user_subscription_plan(user_id)),
            "autosave": bool(body.get("autosave")),
        })
    except Exception:
        return _api_error(500, "Unable to save resume.", code="save_failed")


def api_delete_resume(resume_id: int):
    user_id = _require_api_user_id()
    if user_id is None:
        return _api_error(401, "Authentication required.", code="auth_required")

    resume = get_owned_resume(resume_id, user_id)
    if resume is None:
        return _api_error(403, "You cannot delete this resume.", code="ownership_violation")

    try:
        delete_resume(resume)
        return jsonify({"success": True})
    except Exception:
        return _api_error(500, "Unable to delete resume.", code="delete_failed")


def api_duplicate_resume(resume_id: int):
    user_id = _require_api_user_id()
    if user_id is None:
        return _api_error(401, "Authentication required.", code="auth_required")

    resume = get_owned_resume(resume_id, user_id)
    if resume is None:
        return _api_error(403, "You cannot duplicate this resume.", code="ownership_violation")

    try:
        clone = duplicate_resume(resume)
        plan = _user_subscription_plan(user_id)
        if not can_use_template(clone.template, plan):
            update_resume(clone, template=DEFAULT_TEMPLATE)
        return jsonify({"success": True, "resume": _resume_payload(clone, plan)}), 201
    except Exception:
        return _api_error(500, "Unable to duplicate resume.", code="duplicate_failed")


def api_analyze_resume(resume_id: int):
    user_id = _require_api_user_id()
    if user_id is None:
        return _api_error(401, "Authentication required.", code="auth_required")

    resume = get_owned_resume(resume_id, user_id)
    if resume is None:
        return _api_error(403, "You cannot analyze this resume.", code="ownership_violation")

    body = request.get_json(silent=True) or {}
    job_description = str(body.get("job_description") or "").strip()

    content = sanitize_content(resume.get_content())
    text = _content_to_text(content)
    personal = content.get("personal_information") or {}

    if not text:
        return _api_error(422, "Resume content is empty.", code="empty_resume")

    try:
        ats = analyze_ats(
            resume_text=text,
            name=personal.get("full_name") or None,
            email=personal.get("email") or None,
            phone=personal.get("phone") or None,
            job_description=job_description or None,
        )

        match_result = None
        suggested_skills: List[Dict[str, Any]] = []
        if job_description:
            match_result = match_resume_to_job(text, job_description)
            existing = {str(skill).casefold() for skill in content.get("skills") or []}
            missing_candidates = match_result.get("missing_candidates") or []
            for candidate in missing_candidates:
                candidate_name = str(candidate).strip()
                if candidate_name and candidate_name.casefold() not in existing:
                    suggested_skills.append({
                        "name": candidate_name,
                        "suggested": True,
                        "reason": "Mentioned in job description but not evidenced in your resume yet.",
                    })

        intelligence = _build_resume_intelligence(content, ats, match_result, job_description)

        return jsonify({
            "success": True,
            "ats": ats,
            "match": match_result,
            "skill_suggestions": suggested_skills,
            "intelligence": intelligence,
            "recommendations": intelligence.get("recommendations") or [],
        })
    except ValueError as exc:
        return _api_error(422, str(exc), code="invalid_analysis_input")
    except Exception:
        return _api_error(500, "Unable to analyze resume.", code="analysis_failed")


def api_resume_agent(resume_id: int):
    user_id = _require_api_user_id()
    if user_id is None:
        return _api_error(401, "Authentication required.", code="auth_required")

    resume = get_owned_resume(resume_id, user_id)
    if resume is None:
        return _api_error(403, "You cannot use the agent with this resume.", code="ownership_violation")

    body = request.get_json(silent=True) or {}
    message = str(body.get("message") or "").strip()[:2000]
    job_description = str(body.get("job_description") or "").strip()[:20000]
    if not message:
        return _api_error(422, "Enter a question for the resume assistant.", code="empty_message")

    content = sanitize_content(resume.get_content())
    resume_text = _content_to_text(content)
    try:
        try:
            agent_service = get_agent_service()
        except RuntimeError:
            agent_service = initialize_agent_service()

        user = db.session.get(User, user_id)
        plan = str(user.subscription_plan or "free").strip().lower() if user else "free"
        available_tools = set(agent_service.tool_registry.names())
        grounded_tools = available_tools & {
            "resume", "ats", "job_match", "skill_gap", "recommendation"
        }
        response = agent_service.run(
            message=message,
            resume_text=resume_text,
            job_description=job_description or None,
            user_id=str(user_id),
            session_id=str(session.get("_id") or user_id),
            conversation_id=f"resume:{resume.id}",
            plan=plan if plan in {"free", "pro", "business", "enterprise"} else "free",
            mode="tailor" if job_description else "optimize",
            organization_allowed_tools=grounded_tools,
            context={
                "source": "resume_creation",
                "active_resume": {
                    "id": resume.id,
                    "title": resume.title,
                    "target_role": resume.target_role,
                    "content": content,
                },
            },
            metadata={"resume_id": resume.id, "source": "resume_creation"},
        )
        return jsonify({"success": True, "response": response.to_dict()})
    except Exception:
        return _api_error(503, "The resume assistant is unavailable right now.", code="agent_unavailable")


def api_generate_resume_content(resume_id: int):
    user_id = _require_api_user_id()
    if user_id is None:
        return _api_error(401, "Authentication required.", code="auth_required")

    resume = get_owned_resume(resume_id, user_id)
    if resume is None:
        return _api_error(403, "You cannot generate content for this resume.", code="ownership_violation")

    body = request.get_json(silent=True) or {}
    operation = str(body.get("operation") or "").strip().lower()
    job_description = str(body.get("job_description") or "").strip()
    target_role = str(body.get("target_role") or resume.target_role or "").strip()

    content = sanitize_content(resume.get_content())
    resume_text = _content_to_text(content)
    source_text = _get_resume_source_for_generation(content, body)
    personal = content.get("personal_information") or {}

    resume_data = {
        "name": personal.get("full_name") or session.get("name") or "",
        "skills": content.get("skills") or [],
        "profession_field": personal.get("professional_title") or session.get("profession_field") or "Professional",
        "sections_found": content.get("section_order") or [],
        "word_count": len(resume_text.split()),
        "text": resume_text,
    }

    instruction_overrides = {
        "rewrite_summary": "Rewrite the summary to be more polished and professional.",
        "professional_summary": "Make the summary more professional and impactful.",
        "concise_summary": "Make the summary concise while preserving candidate facts.",
        "tailor_summary": "Tailor this summary for the job description using only candidate evidence.",
        "generate_objective": "Write a concise career objective based only on documented resume facts and the user's target role.",
        "tailor_objective": "Tailor this career objective to the job description using only candidate evidence.",
        "improve_summary_keywords": "Improve ATS keyword alignment in this summary using only true candidate facts.",
        "improve_experience": "Improve the impact and clarity of these bullets without inventing metrics.",
        "project_improve": "Improve this project description professionally without adding unsupported claims.",
        "rewrite_resume_professional": "Rewrite the full resume in a professional tone and preserve all facts.",
        "rewrite_resume_concise": "Rewrite the full resume to be concise and ATS-friendly while preserving facts.",
        "tailor_resume": "Tailor this resume to the job description without adding unsupported skills or achievements.",
    }

    task_map = {
        "generate_summary": TASK_SUMMARY,
        "rewrite_summary": TASK_SUMMARY,
        "professional_summary": TASK_SUMMARY,
        "concise_summary": TASK_SUMMARY,
        "tailor_summary": TASK_SUMMARY,
        "generate_objective": TASK_SUMMARY,
        "tailor_objective": TASK_SUMMARY,
        "improve_summary_keywords": TASK_SUMMARY,
        "generate_experience_bullets": TASK_BULLETS,
        "improve_experience": TASK_EXPERIENCE,
        "project_improve": TASK_EXPERIENCE,
        "rewrite_resume_professional": TASK_RESUME_REWRITE,
        "rewrite_resume_concise": TASK_RESUME_REWRITE,
        "tailor_resume": TASK_RESUME_REWRITE,
    }

    task = task_map.get(operation)
    if task is None:
        return _api_error(422, "Unsupported AI operation.", code="invalid_operation")

    if operation in {"tailor_summary", "tailor_objective", "tailor_resume"} and not job_description:
        return _api_error(422, "Job description is required for tailoring.", code="missing_job_description")

    if task in {TASK_BULLETS, TASK_EXPERIENCE} and not source_text:
        return _api_error(422, "Source text is required for this operation.", code="missing_source_text")

    instructions = str(body.get("instructions") or "").strip()
    if not instructions and operation in instruction_overrides:
        instructions = instruction_overrides[operation]

    try:
        recommendations: List[Dict[str, Any]] = []
        if job_description:
            try:
                ats_preview = analyze_ats(
                    resume_text=resume_text,
                    name=personal.get("full_name") or None,
                    email=personal.get("email") or None,
                    phone=personal.get("phone") or None,
                    job_description=job_description or None,
                )
                match_preview = match_resume_to_job(resume_text, job_description)
                intelligence_preview = _build_resume_intelligence(content, ats_preview, match_preview, job_description)
                recommendations = intelligence_preview.get("recommendations") or []
            except Exception:
                recommendations = []

        apply_mode = body.get("apply") is True
        generated_content = str(body.get("generated_content") or "").strip()

        if apply_mode and generated_content:
            generated = generated_content
        else:
            generated = local_generate(
                task=task,
                resume_data=resume_data,
                source_text=source_text or None,
                job_description=job_description or None,
                target_role=target_role or None,
                instructions=instructions or None,
                recommendations=recommendations,
            )

        claim_validation = validate_generated_claims(resume_text, generated)

        if apply_mode:
            if not claim_validation.get("valid", False):
                return _api_error(
                    422,
                    "This suggestion contains numeric claims not supported by the resume.",
                    code="unsupported_claims",
                )
            _apply_generated_content(resume, body, generated)
            create_resume_version(
                resume,
                action="ai_apply",
                note=f"AI apply operation: {operation}",
            )

        return jsonify({
            "success": True,
            "operation": operation,
            "content": generated,
            "warnings": claim_validation.get("warnings") or [],
            "unsupported_numeric_claims": claim_validation.get("unsupported_numeric_claims") or [],
            "recommendations_used": len(recommendations),
            "applied": bool(body.get("apply")),
            "resume": _resume_payload(resume),
        })
    except Exception:
        return _api_error(500, "Unable to generate content.", code="generation_failed")


def api_list_resume_versions(resume_id: int):
    user_id = _require_api_user_id()
    if user_id is None:
        return _api_error(401, "Authentication required.", code="auth_required")

    resume = get_owned_resume(resume_id, user_id)
    if resume is None:
        return _api_error(403, "You cannot access versions for this resume.", code="ownership_violation")

    versions = [
        {
            "id": version.id,
            "action": version.action,
            "note": version.note,
            "title": version.title,
            "template": version.template,
            "created_at": version.created_at.isoformat() if version.created_at else None,
        }
        for version in list_versions_for_resume(resume.id, user_id)
    ]

    return jsonify({"success": True, "versions": versions})


def api_create_resume_version(resume_id: int):
    user_id = _require_api_user_id()
    if user_id is None:
        return _api_error(401, "Authentication required.", code="auth_required")

    resume = get_owned_resume(resume_id, user_id)
    if resume is None:
        return _api_error(403, "You cannot version this resume.", code="ownership_violation")

    body = request.get_json(silent=True) or {}
    note = str(body.get("note") or "").strip()

    version = create_resume_version(
        resume,
        action="manual_version",
        note=note or "Manual version snapshot",
    )
    return jsonify({
        "success": True,
        "version": {
            "id": version.id,
            "action": version.action,
            "note": version.note,
            "created_at": version.created_at.isoformat() if version.created_at else None,
        },
    }), 201


def api_restore_resume_version(resume_id: int, version_id: int):
    user_id = _require_api_user_id()
    if user_id is None:
        return _api_error(401, "Authentication required.", code="auth_required")

    resume = get_owned_resume(resume_id, user_id)
    if resume is None:
        return _api_error(403, "You cannot restore this resume.", code="ownership_violation")

    version = get_owned_resume_version(version_id, user_id)
    if version is None or version.resume_id != resume.id:
        return _api_error(404, "Resume version not found.", code="version_not_found")

    access_error = _template_access_error(version.template, user_id)
    if access_error:
        return access_error

    restore_resume_from_version(resume, version)
    create_resume_version(
        resume,
        action="restore",
        note=f"Restored from version #{version.id}",
    )

    return jsonify({"success": True, "resume": _resume_payload(resume, _user_subscription_plan(user_id))})


def api_export_resume_pdf(resume_id: int):
    user_id = _require_api_user_id()
    if user_id is None:
        return _api_error(401, "Authentication required.", code="auth_required")

    resume = get_owned_resume(resume_id, user_id)
    if resume is None:
        return _api_error(403, "You cannot export this resume.", code="ownership_violation")

    access_error = _template_access_error(resume.template, user_id)
    if access_error:
        return access_error

    try:
        payload = _export_pdf_bytes(resume)
        filename = f"{_filename_safe(resume.title)}.pdf"
        return send_file(
            io.BytesIO(payload),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename,
        )
    except Exception:
        return _api_error(500, "Unable to export PDF.", code="pdf_export_failed")


def api_export_resume_docx(resume_id: int):
    user_id = _require_api_user_id()
    if user_id is None:
        return _api_error(401, "Authentication required.", code="auth_required")

    resume = get_owned_resume(resume_id, user_id)
    if resume is None:
        return _api_error(403, "You cannot export this resume.", code="ownership_violation")

    access_error = _template_access_error(resume.template, user_id)
    if access_error:
        return access_error

    try:
        payload = _export_docx_bytes(resume)
        filename = f"{_filename_safe(resume.title)}.docx"
        return send_file(
            io.BytesIO(payload),
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            as_attachment=True,
            download_name=filename,
        )
    except Exception:
        return _api_error(500, "Unable to export DOCX.", code="docx_export_failed")

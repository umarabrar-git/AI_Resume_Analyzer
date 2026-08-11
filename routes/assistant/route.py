from flask import Blueprint, jsonify, redirect, request, session, url_for

from routes.auth import login_required
from services.resume_intelligence.agents import get_agent_service, initialize_agent_service

from .view import render_assistant


def _normalize_session_value(value):
    if value is None:
        return None
    if isinstance(value, (list, tuple, set)):
        return [str(item) for item in value if item is not None]
    if isinstance(value, dict):
        return value
    return value


def _extract_analysis_context(session_obj):
    analysis_payload = session_obj.get("analysis_result", {}) or {}
    if isinstance(analysis_payload, dict) and isinstance(analysis_payload.get("analysis_result"), dict):
        analysis_payload = analysis_payload.get("analysis_result")

    if not isinstance(analysis_payload, dict):
        return {}

    normalized = {}
    for key, value in analysis_payload.items():
        if isinstance(value, dict):
            normalized[key] = value
        elif isinstance(value, list):
            normalized[key] = value
        else:
            normalized[key] = value

    return normalized


def _extract_resume_context(session_obj):
    analysis_payload = _extract_analysis_context(session_obj)
    resume_context = {
        "ats_score": session_obj.get("ats_score"),
        "matched_skills": session_obj.get("matched_skills", []),
        "missing_skills": session_obj.get("missing_skills", []),
        "profession_field": session_obj.get("profession_field"),
        "profile_strength": session_obj.get("profile_strength"),
        "recommendations": session_obj.get("recommendations", []),
    }

    for fallback_key in ("text", "resume_content", "resume_text"):
        fallback_value = session_obj.get(fallback_key)
        if fallback_value:
            resume_context["resume_text_fallback"] = fallback_value
            break

    if analysis_payload:
        ats = analysis_payload.get("ats") or analysis_payload.get("ats_result") or {}
        match = analysis_payload.get("job_match") or analysis_payload.get("matching") or {}
        recommendations = analysis_payload.get("recommendations")

        if isinstance(ats, dict):
            ats_score = ats.get("ats_score")
            if ats_score is not None:
                resume_context["ats_score"] = ats_score

        if isinstance(match, dict):
            matched_skills = match.get("matched_skills") or match.get("matched_required") or match.get("matched")
            missing_skills = match.get("missing_skills") or match.get("missing_required") or match.get("missing")
            if matched_skills is not None:
                resume_context["matched_skills"] = matched_skills
            if missing_skills is not None:
                resume_context["missing_skills"] = missing_skills

        if recommendations is not None:
            resume_context["recommendations"] = recommendations

    resume_context = {
        key: _normalize_session_value(value)
        for key, value in resume_context.items()
    }
    return resume_context

bp = Blueprint("assistant", __name__)
bp.add_url_rule("/assistant", view_func=render_assistant)


ACTION_MESSAGES = {
    "improve_ats": "Improve my ATS score for this role.",
    "rewrite_summary": "Rewrite my resume summary for this role.",
    "add_skills": "Suggest skills I should add to my resume for this role.",
    "create_resume": "Create a stronger resume strategy for this target role.",
    "generate_cover_letter": "Generate a cover letter for this role based on my resume.",
    "interview_prep": "Prepare interview guidance based on my resume and target role.",
}


@bp.route("/api/agent/chat", methods=["POST"])
def agent_chat():
    if "user_id" not in session:
        return redirect(url_for("auth.login", next=request.path))

    payload = request.get_json(silent=True) or {}
    message = str(payload.get("message", "") or "").strip()
    action = str(payload.get("action", "") or "").strip().lower()

    if not message:
        if action in ACTION_MESSAGES:
            message = ACTION_MESSAGES[action]
        else:
            return jsonify(
                {
                    "success": False,
                    "content": "Please provide a message or choose a quick action.",
                    "intent": None,
                    "confidence": 0.0,
                    "warnings": [],
                    "errors": ["empty request"],
                    "metadata": {"stage": "route_validation"},
                }
            ), 400

    resume_text = str(session.get("resume_text", "") or "").strip()
    if not resume_text:
        fallback_resume_text = ""
        for fallback_key in ("text", "resume_content"):
            fallback_value = session.get(fallback_key)
            if isinstance(fallback_value, str) and fallback_value.strip():
                fallback_resume_text = fallback_value.strip()
                break
        if fallback_resume_text:
            resume_text = fallback_resume_text

    job_description = str(session.get("job_description", "") or "").strip()

    if not resume_text:
        return jsonify(
            {
                "success": False,
                "content": "Please upload and analyze a resume before using the assistant. Once your resume is available, I can help improve ATS alignment, rewrite your summary, and suggest skills.",
                "intent": None,
                "confidence": 0.0,
                "warnings": [],
                "errors": ["resume context required"],
                "metadata": {"stage": "route_validation"},
            }
        ), 200

    try:
        agent_service = get_agent_service()
    except RuntimeError:
        agent_service = initialize_agent_service()

    analysis_payload = _extract_analysis_context(session)
    resume_context = _extract_resume_context(session)

    conversation_id = session.get("assistant_conversation_id")
    if not conversation_id:
        conversation_id = f"assistant:{session.get('user_id') or 'anonymous'}"
        session["assistant_conversation_id"] = conversation_id
        session.modified = True

    response = agent_service.run(
        message=message,
        resume_text=resume_text,
        job_description=job_description or None,
        user_id=str(session.get("user_id") or "") or None,
        session_id=str(session.get("_id") or session.get("user_id") or "") or None,
        conversation_id=conversation_id,
        context={
            "source": "assistant_ui",
            "session_analysis": analysis_payload,
            "resume_context": resume_context,
            "action": action or None,
        },
        metadata={
            "source": "assistant_ui",
            "action": action or None,
            "session_id": str(session.get("_id") or session.get("user_id") or "") or None,
        },
    )

    return jsonify(response.to_dict())

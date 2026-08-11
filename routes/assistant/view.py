from flask import render_template, session

from utils import build_session_context


def render_assistant():
    context = build_session_context(session)
    context["has_analysis"] = bool(session.get("ats_score") or session.get("resume_text"))
    return render_template("assistant.html", **context)

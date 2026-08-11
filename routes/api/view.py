from __future__ import annotations

import json

from flask import (
    jsonify,
    request,
    session,
)

from routes.auth import login_required
from utils import build_session_context

from services.resume_intelligence.generative.local_generation import (
    TASK_BULLETS,
    TASK_COVER_LETTER,
    TASK_EXPERIENCE,
    TASK_RESUME_REWRITE,
    TASK_SUMMARY,
    local_generate,
)
from services.resume_intelligence.generative.assistant_engine import (
    get_assistant_response,
)


# ---------------------------------------------------------------------------
# /api/generate
# ---------------------------------------------------------------------------

@login_required
def api_generate():
    """
    Generate resume content using the local AI engine.

    Expected JSON body:
        {
            "task":            "summary" | "bullets" | "experience_rewrite"
                               | "resume_rewrite" | "cover_letter",
            "source_text":     "...",   # optional — text to rewrite
            "target_role":     "...",   # optional
            "job_description": "...",   # optional override
            "instructions":    "...",   # optional free-text
        }

    Returns:
        { "success": true, "content": "..." }
    """
    try:
        body = request.get_json(silent=True) or {}
        task = (body.get("task") or "").strip().lower()

        valid_tasks = {
            TASK_SUMMARY, TASK_BULLETS, TASK_EXPERIENCE,
            TASK_RESUME_REWRITE, TASK_COVER_LETTER,
        }

        if task not in valid_tasks:
            return jsonify(
                success=False,
                error=f"Invalid task '{task}'. Valid tasks: {sorted(valid_tasks)}"
            ), 400

        resume_data = build_session_context(session)

        # Allow per-request JD override
        job_description = (
            body.get("job_description")
            or session.get("job_description")
            or ""
        )

        content = local_generate(
            task=task,
            resume_data=resume_data,
            source_text=body.get("source_text"),
            job_description=job_description,
            target_role=body.get("target_role"),
            instructions=body.get("instructions"),
            recommendations=resume_data.get("recommendations") or [],
        )

        return jsonify(success=True, content=content)

    except Exception as exc:
        return jsonify(success=False, error=str(exc)), 500


# ---------------------------------------------------------------------------
# /api/assistant/chat
# ---------------------------------------------------------------------------

def api_assistant_chat():
    """
    AI Career Assistant chat endpoint.

    Expected JSON body:
        {
            "message":  "...",
            "history":  [{"role": "user"|"assistant", "content": "..."}]  # optional
        }

    Returns:
        { "success": true, "response": "...", "intent": "..." }
    """
    try:
        body = request.get_json(silent=True) or {}
        message = (body.get("message") or "").strip()
        history = body.get("history") or []

        resume_data = build_session_context(session)

        response_text = get_assistant_response(
            message=message,
            resume_data=resume_data,
            conversation_history=history,
        )

        return jsonify(
            success=True,
            response=response_text,
        )

    except Exception as exc:
        return jsonify(success=False, error=str(exc)), 500

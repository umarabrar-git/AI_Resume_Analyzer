from flask import render_template, session

from utils import build_session_context
from services.resume_intelligence.adapters import AnalysisUIAdapter

ui_adapter = AnalysisUIAdapter()


def render_reports():
    context = build_session_context(session)
    analysis_result = session.get("analysis_result", {})
    resume_text = session.get("resume_text", "")
    job_description = session.get("job_description", "")

    has_analysis = bool(analysis_result) and bool(resume_text)

    if has_analysis:
        ui_context = ui_adapter.build(
            analysis_result,
            resume_text=resume_text,
            job_description=job_description,
        )
        for key, value in ui_context.items():
            if value or value == 0:
                context[key] = value

    context["has_analysis"] = has_analysis
    return render_template("reports.html", **context)

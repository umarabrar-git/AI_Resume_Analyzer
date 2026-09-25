from flask import (
    render_template,
    request,
    session,
)

from routes.auth import login_required
from utils import build_session_context

from services.resume_intelligence.adapters import (
    AnalysisUIAdapter,
)


ui_adapter = AnalysisUIAdapter()


@login_required
def render_analysis():
    """
    Render the Resume Intelligence analysis dashboard.
    """

    context = build_session_context(
        session
    )

    analysis_result = session.get(
        "analysis_result",
        {}
    )

    resume_text = session.get(
        "resume_text",
        ""
    )

    job_description = session.get(
        "job_description",
        ""
    )

    # Only run the UI adapter when there is real analysis data.
    # If the adapter would just return zeros (no resume uploaded),
    # keep the session context values intact instead.
    has_analysis = bool(analysis_result) and bool(resume_text)
    upload_requested = request.args.get("upload") == "1"

    if has_analysis:
        ui_context = ui_adapter.build(
            analysis_result,
            resume_text=resume_text,
            job_description=job_description,
        )
        # Merge: only overwrite session values with adapter values
        # that are non-zero / non-empty so we don't blank real data.
        for key, value in ui_context.items():
            if value or value == 0:
                context[key] = value

    context["has_analysis"] = has_analysis and not upload_requested

    return render_template(
        "analysis.html",
        **context,
    )
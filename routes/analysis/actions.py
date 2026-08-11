from __future__ import annotations

from flask import (
    flash,
    redirect,
    request,
    session,
    url_for,
)

from routes.auth import login_required

from services.resume_intelligence.workflows import (
    AnalysisWorkflow,
    AnalysisWorkflowRequest,
)


workflow = AnalysisWorkflow()


@login_required
def run_analysis():
    """
    Execute the complete AI resume analysis workflow.
    """

    resume_text = request.form.get(
        "resume_text",
        ""
    ).strip()

    job_description = request.form.get(
        "job_description",
        ""
    ).strip()

    if not resume_text:
        flash(
            "Resume content is required.",
            "error"
        )

        return redirect(
            url_for(
                "analysis.render_analysis"
            )
        )

    try:
        workflow_request = (
            AnalysisWorkflowRequest(
                resume_text=resume_text,

                job_description=(
                    job_description
                    or None
                ),

                user_id=str(
                    session.get(
                        "user_id",
                        ""
                    )
                ) or None,

                session_id=str(
                    session.get(
                        "_id",
                        ""
                    )
                ) or None,

                context={
                    "source":
                        "analysis_page",

                    "authenticated":
                        True,
                },

                metadata={
                    "feature":
                        "resume_analysis",

                    "interface":
                        "web",
                },
            )
        )

        result = workflow.run(
            workflow_request
        )

        # Convert response into a session-safe structure.
        if hasattr(
            result,
            "to_dict"
        ):
            result_data = (
                result.to_dict()
            )

        elif hasattr(
            result,
            "__dict__"
        ):
            result_data = dict(
                result.__dict__
            )

        else:
            result_data = result

        session[
            "analysis_result"
        ] = result_data

        # Keep input available for dashboard/results.
        session[
            "resume_text"
        ] = resume_text

        session[
            "job_description"
        ] = job_description

        session.modified = True

        flash(
            "Resume analysis completed successfully.",
            "success"
        )

    except ValueError as exc:

        flash(
            str(exc),
            "error"
        )

    except Exception:

        flash(
            "The resume analysis could not be completed.",
            "error"
        )

    return redirect(
        url_for(
            "analysis.render_analysis"
        )
    )
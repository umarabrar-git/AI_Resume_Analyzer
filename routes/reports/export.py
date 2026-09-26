from __future__ import annotations

from flask import (
    Blueprint,
    Response,
    jsonify,
    request,
    send_file,
    session,
)

from utils.report_export import (
    docx_exporter,
    pdf_exporter,
    report_data_builder,
)


bp = Blueprint(
    "reports_export",
    __name__,
    url_prefix="/reports/export",
)


FREE_TEMPLATES = {
    "professional",
    "modern",
    "minimal",
}


PREMIUM_TEMPLATES = {
    "executive",
    "ai_insights",
    "career_analytics",
}


ALL_TEMPLATES = (
    FREE_TEMPLATES
    | PREMIUM_TEMPLATES
)


def _get_report_context():
    """
    Uses the same session-backed analysis state as the existing
    reports view.
    """

    analysis_result = session.get(
        "analysis_result"
    )

    resume_text = session.get(
        "resume_text",
        "",
    )

    job_description = session.get(
        "job_description",
        "",
    )

    if not isinstance(
        analysis_result,
        dict,
    ):
        return None

    if not resume_text:
        return None

    return (
        analysis_result,
        resume_text,
        job_description,
    )


def _user_has_premium_access() -> bool:
    """
    Reads an existing session entitlement if one exists.

    No fake subscription/database lookup is introduced here.
    Until the project's actual billing/entitlement system is wired,
    premium exports remain protected.
    """

    return bool(
        session.get("is_premium")
        or session.get("premium")
        or session.get("subscription_tier")
        in {
            "premium",
            "pro",
            "business",
            "enterprise",
        }
    )


def _validate_template(
    template: str,
):
    template = (
        template
        or "professional"
    ).strip().lower()

    if template not in ALL_TEMPLATES:
        return (
            None,
            jsonify(
                {
                    "success": False,
                    "error": "Invalid report template.",
                }
            ),
            400,
        )

    if (
        template in PREMIUM_TEMPLATES
        and not _user_has_premium_access()
    ):
        return (
            None,
            jsonify(
                {
                    "success": False,
                    "error": (
                        "This report template requires "
                        "a premium subscription."
                    ),
                    "code": "premium_required",
                }
            ),
            403,
        )

    return template, None, None


def _build_report():
    context = _get_report_context()

    if context is None:
        return None

    (
        analysis_result,
        resume_text,
        job_description,
    ) = context

    return report_data_builder.build(
        analysis_result,
        resume_text=resume_text,
        job_description=job_description,
        name=session.get(
            "name",
            "",
        ),
    )


@bp.post("/pdf")
def export_pdf():
    template, error, status = _validate_template(
        request.form.get(
            "template",
            "professional",
        )
    )

    if error is not None:
        return error, status

    report = _build_report()

    if report is None:
        return (
            jsonify(
                {
                    "success": False,
                    "error": (
                        "No completed resume analysis "
                        "is available."
                    ),
                }
            ),
            404,
        )

    try:
        file_stream = pdf_exporter.export(
            report,
            template=template,
        )

    except ValueError as exc:
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(exc),
                }
            ),
            400,
        )

    except Exception:
        return (
            jsonify(
                {
                    "success": False,
                    "error": (
                        "The PDF report could not "
                        "be generated."
                    ),
                }
            ),
            500,
        )

    filename = (
        "resume_analysis_report_"
        f"{template}.pdf"
    )

    return send_file(
        file_stream,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )


@bp.post("/docx")
def export_docx():
    template, error, status = _validate_template(
        request.form.get(
            "template",
            "professional",
        )
    )

    if error is not None:
        return error, status

    report = _build_report()

    if report is None:
        return (
            jsonify(
                {
                    "success": False,
                    "error": (
                        "No completed resume analysis "
                        "is available."
                    ),
                }
            ),
            404,
        )

    try:
        file_stream = docx_exporter.export(
            report,
            template=template,
        )

    except ValueError as exc:
        return (
            jsonify(
                {
                    "success": False,
                    "error": str(exc),
                }
            ),
            400,
        )

    except Exception:
        return (
            jsonify(
                {
                    "success": False,
                    "error": (
                        "The DOCX report could not "
                        "be generated."
                    ),
                }
            ),
            500,
        )

    filename = (
        "resume_analysis_report_"
        f"{template}.docx"
    )

    return send_file(
        file_stream,
        mimetype=(
            "application/vnd.openxmlformats-"
            "officedocument.wordprocessingml.document"
        ),
        as_attachment=True,
        download_name=filename,
    )
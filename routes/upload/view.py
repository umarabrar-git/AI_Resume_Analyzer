from __future__ import annotations

import os
import logging

from flask import (
    current_app,
    flash,
    redirect,
    request,
    session,
    url_for,
)
from werkzeug.utils import secure_filename

from routes.auth import login_required

from services.resume_intelligence.workflows import (
    AnalysisWorkflow,
    AnalysisWorkflowRequest,
)

from utils import (
    allowed_file,
    extract_resume_text,
)
from utils.dashboard.dashboard_context import apply_analysis_to_session


analysis_workflow = AnalysisWorkflow()
logger = logging.getLogger(__name__)


def _is_placeholder_text(text: str) -> bool:
    normalized = (text or "").strip().lower()
    return normalized in {
        "[pdf parsing requires pymupdf - not installed]",
        "pdf resume uploaded",
        "resume text",
    }


@login_required
def upload_resume():
    """
    Upload resume, extract its text and execute
    the Resume Intelligence analysis workflow.
    """

    resume = request.files.get("resume")

    job_description = request.form.get(
        "job_description",
        ""
    ).strip()

    current_app.logger.info(
        "[UPLOAD] filename=%s job_description_present=%s content_type=%s",
        getattr(resume, "filename", None),
        bool(job_description),
        getattr(resume, "content_type", None),
    )

    # -----------------------------------------
    # Validate upload
    # -----------------------------------------

    if resume is None:
        flash(
            "Please select a resume.",
            "error"
        )

        return redirect(
            url_for("home.render_home")
        )

    if not resume.filename:
        flash(
            "Please select a resume.",
            "error"
        )

        return redirect(
            url_for("home.render_home")
        )

    if not allowed_file(
        resume.filename,
        current_app.config[
            "ALLOWED_EXTENSIONS"
        ],
    ):
        flash(
            "Unsupported resume file type.",
            "error"
        )

        return redirect(
            url_for("home.render_home")
        )

    # -----------------------------------------
    # Secure filename
    # -----------------------------------------

    filename = secure_filename(
        resume.filename
    )

    extension = (
        filename
        .rsplit(".", 1)[1]
        .lower()
    )

    upload_folder = (
        current_app.config[
            "UPLOAD_FOLDER"
        ]
    )

    os.makedirs(
        upload_folder,
        exist_ok=True,
    )

    filepath = os.path.join(
        upload_folder,
        filename,
    )

    current_app.logger.info(
        "[UPLOAD] save_location=%s extension=%s",
        filepath,
        extension,
    )

    try:

        # -------------------------------------
        # Save resume
        # -------------------------------------

        resume.save(filepath)

        file_size = os.path.getsize(filepath)
        current_app.logger.info(
            "[UPLOAD] saved=True file_size=%s",
            file_size,
        )

        # -------------------------------------
        # Extract resume text
        # -------------------------------------

        current_app.logger.info(
            "[PARSER] parser=%s",
            "pdf" if extension == "pdf" else "docx" if extension == "docx" else "unknown",
        )

        resume_text = extract_resume_text(
            filepath,
            extension,
        )

        if not resume_text or _is_placeholder_text(resume_text):
            flash(
                "We couldn't extract readable text from this resume.",
                "error"
            )

            current_app.logger.warning(
                "[PARSER] failed file=%s extension=%s chars=%s words=%s",
                filename,
                extension,
                len(resume_text or ""),
                len((resume_text or "").split()),
            )

            return redirect(
                url_for(
                    "home.render_home"
                )
            )

        resume_text = resume_text.strip()

        current_app.logger.info(
            "[PARSER] chars=%s words=%s head=%s",
            len(resume_text),
            len(resume_text.split()),
            resume_text[:200].replace("\n", " | "),
        )

        # -------------------------------------
        # Build AI workflow request
        # -------------------------------------

        current_app.logger.info(
            "[ANALYSIS] starting filename=%s chars=%s words=%s",
            filename,
            len(resume_text),
            len(resume_text.split()),
        )

        workflow_request = (
            AnalysisWorkflowRequest(
                resume_text=resume_text,

                job_description=(
                    job_description
                    or None
                ),

                user_id=(
                    str(
                        session.get(
                            "user_id"
                        )
                    )
                    if session.get(
                        "user_id"
                    )
                    else None
                ),

                context={
                    "source":
                        "resume_upload",

                    "filename":
                        filename,

                    "file_type":
                        extension,
                },

                metadata={
                    "feature":
                        "resume_analysis",

                    "interface":
                        "web",

                    "has_job_description":
                        bool(
                            job_description
                        ),
                },
            )
        )

        # -------------------------------------
        # Execute Agentic AI workflow
        # -------------------------------------

        result = (
            analysis_workflow.run(
                workflow_request
            )
        )

        # -------------------------------------
        # Convert response for Flask session
        # -------------------------------------

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

        analysis_result = result_data.get("analysis_result", {}) if isinstance(result_data, dict) else {}
        ats_score = 0
        detected_skills = 0
        if isinstance(analysis_result, dict):
            ats_block = analysis_result.get("ats", {}) or analysis_result.get("ats_result", {})
            resume_block = analysis_result.get("resume", {}) or {}
            job_match_block = analysis_result.get("job_match", {}) or {}
            ats_score = ats_block.get("ats_score", 0) if isinstance(ats_block, dict) else 0
            detected_skills = len(resume_block.get("skills", [])) if isinstance(resume_block, dict) else 0
            current_app.logger.info(
                "[ANALYSIS] completed ats_score=%s skills=%s match_percentage=%s",
                ats_score,
                detected_skills,
                job_match_block.get("match_percentage", 0) if isinstance(job_match_block, dict) else 0,
            )

        # -------------------------------------
        # Store result
        # -------------------------------------

        session[
            "analysis_result"
        ] = result_data

        apply_analysis_to_session(
            session,
            result_data,
            resume_text=resume_text,
            job_description=job_description,
        )

        session[
            "resume_text"
        ] = resume_text

        session[
            "job_description"
        ] = job_description

        session[
            "resume_filename"
        ] = filename

        session.modified = True

        flash(
            "Resume analyzed successfully.",
            "success"
        )

        # -------------------------------------
        # Open analysis dashboard
        # -------------------------------------

        return redirect(
            url_for(
                "analysis.render_analysis"
            )
        )

    except ValueError as exc:

        current_app.logger.warning(
            "Resume analysis validation error: %s",
            exc,
        )

        flash(
            str(exc),
            "error"
        )

        return redirect(
            url_for(
                "home.render_home"
            )
        )

    except Exception:

        current_app.logger.exception(
            "Resume analysis failed."
        )

        flash(
            "Resume analysis could not be completed.",
            "error"
        )

        return redirect(
            url_for(
                "home.render_home"
            )
        )

    finally:

        # -------------------------------------
        # Remove temporary resume
        # -------------------------------------

        try:
            if os.path.exists(
                filepath
            ):
                os.remove(
                    filepath
                )

        except OSError:
            current_app.logger.warning(
                "Unable to remove temporary "
                "resume file: %s",
                filepath,
            )
import hmac

from flask import Blueprint, jsonify, request, session

from .view import (
	api_analyze_resume,
	api_create_resume,
	api_create_resume_version,
	api_delete_resume,
	api_duplicate_resume,
	api_export_resume_docx,
	api_export_resume_pdf,
	api_generate_resume_content,
	api_import_resume,
	api_resume_agent,
	api_get_resume,
	api_list_resume_versions,
	api_list_resumes,
	api_restore_resume_version,
	api_update_resume,
	render_resume_creation,
)

bp = Blueprint("resume_creation", __name__)


@bp.before_request
def protect_resume_creation_mutations():
	if not request.path.startswith("/resume-creation/api/") or request.method not in {"POST", "PATCH", "DELETE"}:
		return None
	if session.get("user_id") is None:
		return None

	expected = str(session.get("resume_csrf_token") or "")
	provided = str(request.headers.get("X-CSRF-Token") or "")
	if not expected or not provided or not hmac.compare_digest(expected, provided):
		return jsonify({
			"success": False,
			"error": "Invalid or missing CSRF token.",
			"code": "csrf_failed",
		}), 403
	return None


bp.add_url_rule("/resume-creation", view_func=render_resume_creation, methods=["GET"])

bp.add_url_rule("/resume-creation/api/resumes", view_func=api_list_resumes, methods=["GET"])
bp.add_url_rule("/resume-creation/api/resumes", view_func=api_create_resume, methods=["POST"])
bp.add_url_rule("/resume-creation/api/resumes/import", view_func=api_import_resume, methods=["POST"])
bp.add_url_rule("/resume-creation/api/resumes/<int:resume_id>", view_func=api_get_resume, methods=["GET"])
bp.add_url_rule("/resume-creation/api/resumes/<int:resume_id>", view_func=api_update_resume, methods=["PATCH"])
bp.add_url_rule("/resume-creation/api/resumes/<int:resume_id>", view_func=api_delete_resume, methods=["DELETE"])
bp.add_url_rule("/resume-creation/api/resumes/<int:resume_id>/duplicate", view_func=api_duplicate_resume, methods=["POST"])
bp.add_url_rule("/resume-creation/api/resumes/<int:resume_id>/analyze", view_func=api_analyze_resume, methods=["POST"])
bp.add_url_rule("/resume-creation/api/resumes/<int:resume_id>/assistant", view_func=api_resume_agent, methods=["POST"])
bp.add_url_rule("/resume-creation/api/resumes/<int:resume_id>/generate", view_func=api_generate_resume_content, methods=["POST"])
bp.add_url_rule("/resume-creation/api/resumes/<int:resume_id>/versions", view_func=api_list_resume_versions, methods=["GET"])
bp.add_url_rule("/resume-creation/api/resumes/<int:resume_id>/versions", view_func=api_create_resume_version, methods=["POST"])
bp.add_url_rule("/resume-creation/api/resumes/<int:resume_id>/versions/<int:version_id>/restore", view_func=api_restore_resume_version, methods=["POST"])
bp.add_url_rule("/resume-creation/api/resumes/<int:resume_id>/export/pdf", view_func=api_export_resume_pdf, methods=["GET"])
bp.add_url_rule("/resume-creation/api/resumes/<int:resume_id>/export/docx", view_func=api_export_resume_docx, methods=["GET"])

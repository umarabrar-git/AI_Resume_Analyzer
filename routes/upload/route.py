from flask import Blueprint

from .view import upload_resume


bp = Blueprint(
    "upload",
    __name__,
)


bp.add_url_rule(
    "/upload",
    endpoint="upload_resume",
    view_func=upload_resume,
    methods=["POST"],
)
from flask import Blueprint
from .view import render_privacy

privacy_bp = Blueprint(
    "privacy",
    __name__,
    url_prefix="/privacy"
)

privacy_bp.add_url_rule(
    "/",
    endpoint="render_privacy",
    view_func=render_privacy,
    methods=["GET"]
)

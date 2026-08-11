from flask import Blueprint
from .view import render_terms

terms_bp = Blueprint(
    "terms",
    __name__,
    url_prefix="/terms"
)

terms_bp.add_url_rule(
    "/",
    endpoint="render_terms",
    view_func=render_terms,
    methods=["GET"]
)

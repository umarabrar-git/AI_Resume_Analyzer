from flask import Blueprint

from .view import render_about


about_bp = Blueprint(
    "about",
    __name__,
    url_prefix="/about"
)


about_bp.add_url_rule(
    "/",
    endpoint="render_about",
    view_func=render_about,
    methods=["GET"]
)
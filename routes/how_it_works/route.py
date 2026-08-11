from flask import Blueprint
from .view import render_how_it_works

how_it_works_bp = Blueprint(
    "how_it_works",
    __name__,
    url_prefix="/how-it-works"
)

how_it_works_bp.add_url_rule(
    "/",
    view_func=render_how_it_works,
    methods=["GET"]
)
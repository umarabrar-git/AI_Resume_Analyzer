from flask import Blueprint
from .view import render_pricing

pricing_bp = Blueprint(
    "pricing",
    __name__,
    url_prefix="/pricing"
)

pricing_bp.add_url_rule(
    "/",
    view_func=render_pricing,
    methods=["GET"]
)
from flask import Blueprint
from .view import render_features


features_bp = Blueprint(
    "features",
    __name__,
    url_prefix="/features"
)


features_bp.add_url_rule(
    "/",
    view_func=render_features,
    methods=["GET"]
)
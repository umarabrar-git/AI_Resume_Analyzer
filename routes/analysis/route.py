from flask import Blueprint

from .actions import run_analysis
from .view import render_analysis


bp = Blueprint(
    "analysis",
    __name__,
)


bp.add_url_rule(
    "/analysis",
    endpoint="render_analysis",
    view_func=render_analysis,
    methods=["GET"],
)


bp.add_url_rule(
    "/analysis/run",
    endpoint="run_analysis",
    view_func=run_analysis,
    methods=["POST"],
)
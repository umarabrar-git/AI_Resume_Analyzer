from flask import Blueprint

from .view import render_reports

bp = Blueprint("reports", __name__)
bp.add_url_rule("/reports", view_func=render_reports)

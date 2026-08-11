from flask import Blueprint

from .view import render_dashboard

bp = Blueprint("dashboard", __name__)
bp.add_url_rule("/dashboard", view_func=render_dashboard)

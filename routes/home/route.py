from flask import Blueprint

from .view import render_home

bp = Blueprint("home", __name__)
bp.add_url_rule("/", view_func=render_home)

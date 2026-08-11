from flask import Blueprint
from .view import render_faq

faq_bp = Blueprint("faq", __name__, url_prefix="/faq")
faq_bp.add_url_rule("/", endpoint="render_faq", view_func=render_faq, methods=["GET"])

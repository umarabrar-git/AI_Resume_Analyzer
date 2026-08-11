from flask import Blueprint

from .view import render_legal

legal_bp = Blueprint(
	"legal",
	__name__,
	url_prefix="/legal"
)

legal_bp.add_url_rule(
	"/",
	endpoint="render_legal",
	view_func=render_legal,
	methods=["GET"]
)

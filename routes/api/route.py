from flask import Blueprint

from .view import api_generate, api_assistant_chat

bp = Blueprint("api", __name__)

bp.add_url_rule(
    "/api/generate",
    endpoint="generate",
    view_func=api_generate,
    methods=["POST"],
)

bp.add_url_rule(
    "/api/assistant/chat",
    endpoint="assistant_chat",
    view_func=api_assistant_chat,
    methods=["POST"],
)

from flask import render_template, session

from utils import build_session_context


def render_settings():
    return render_template("settings.html", **build_session_context(session))

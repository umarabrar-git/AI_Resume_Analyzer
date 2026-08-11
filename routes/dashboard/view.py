from flask import render_template, session

from routes.auth import login_required
from utils import build_session_context, seed_dashboard_session


@login_required
def render_dashboard():
    if "ats_score" not in session:
        seed_dashboard_session(session)
    return render_template("dashboard.html", **build_session_context(session))

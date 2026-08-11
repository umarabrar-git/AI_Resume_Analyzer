from flask import (
	Blueprint,
	render_template,
	request,
	redirect,
	url_for,
	session,
	flash,
)

from routes.auth import login_required
from services.account.account_service import (
	get_account_user,
	update_profile,
)


bp = Blueprint(
	"settings",
	__name__,
	url_prefix="/settings",
)


@bp.route("/", methods=["GET"])
@login_required
def render_settings():
	"""Render the user's account center."""
	user = get_account_user(session["user_id"])

	if not user:
		session.clear()
		flash(
			"Your session is no longer valid. Please log in again.",
			"warning",
		)
		return redirect(url_for("auth.login"))

	return render_template("settings/settings.html", user=user)


@bp.route("/profile", methods=["POST"])
@login_required
def update_profile_route():
	"""Update the user's profile."""
	user = get_account_user(session["user_id"])

	if not user:
		session.clear()
		return redirect(url_for("auth.login"))

	full_name = request.form.get("full_name", "")
	success, message = update_profile(user, full_name)

	if success:
		session["user_name"] = user.full_name
		flash(message, "success")
	else:
		flash(message, "error")

	return redirect(url_for("settings.render_settings", section="profile"))

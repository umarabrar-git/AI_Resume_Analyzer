from services.auth.auth_service import get_user_by_id
from database import db


def get_account_user(user_id):
    """Return the currently authenticated user."""
    return get_user_by_id(user_id)


def update_profile(user, full_name):
    """Update editable profile information."""
    full_name = (full_name or "").strip()

    if not full_name:
        return False, "Full name is required."

    if len(full_name) < 2:
        return False, "Full name must contain at least 2 characters."

    if len(full_name) > 100:
        return False, "Full name is too long."

    try:
        user.full_name = full_name
        db.session.commit()
        return True, "Profile updated successfully."
    except Exception:
        db.session.rollback()
        return False, "Unable to update profile."

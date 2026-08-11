"""Authentication service for user management."""

from datetime import datetime
from database import db
from models.user import User
from utils.auth.password import validate_password
from utils.auth.validators import validate_email, validate_full_name


def register_user(full_name, email, password, confirm_password):
    """
    Register a new user.
    
    Args:
        full_name: User's full name
        email: User's email
        password: User's password
        confirm_password: Confirmation password
    
    Returns:
        Tuple: (success: bool, message: str, user: User or None)
    """
    # Validate full name
    valid, msg = validate_full_name(full_name)
    if not valid:
        return False, msg, None
    
    # Validate email
    valid, msg = validate_email(email)
    if not valid:
        return False, msg, None
    
    # Check if email already exists
    if user_exists(email):
        return False, "Email already registered. Please login or use a different email.", None
    
    # Validate passwords match
    if password != confirm_password:
        return False, "Passwords do not match", None
    
    # Validate password strength
    valid, msg = validate_password(password)
    if not valid:
        return False, msg, None
    
    # Create new user
    user = User(
        full_name=full_name,
        email=email,
        subscription_plan='free',
        scans_left=5,
        created_at=datetime.now()
    )
    user.set_password(password)
    user.is_authenticated = True
    
    # Persist user to database
    db.session.add(user)
    db.session.commit()
    
    return True, "Registration successful! Welcome to AI Resume Analyzer", user


def login_user(email, password):
    """
    Login a user.
    
    Args:
        email: User's email
        password: User's password
    
    Returns:
        Tuple: (success: bool, message: str, user: User or None)
    """
    # Find user by email
    user = get_user_by_email(email)
    
    if not user:
        return False, "Email not found. Please register first.", None
    
    # Check password
    if not user.check_password(password):
        return False, "Invalid password", None
    
    # Update last login
    user.last_login = datetime.now()
    user.is_authenticated = True
    db.session.commit()
    
    return True, "Login successful!", user


def get_user_by_id(user_id):
    """Get user by ID."""
    return db.session.get(User, user_id)


def get_user_by_email(email):
    """Get user by email (case-insensitive)."""
    return User.query.filter(db.func.lower(User.email) == email.lower()).first()


def logout_user(user_id):
    """Logout a user."""
    user = get_user_by_id(user_id)
    if user:
        user.is_authenticated = False
    return True


def user_exists(email):
    """Check if user exists by email."""
    return get_user_by_email(email) is not None

"""Authentication routes for registration, login, and logout."""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from services.auth.auth_service import register_user, login_user, logout_user, get_user_by_id

bp = Blueprint('auth', __name__, url_prefix='/auth')


def _get_safe_next_url(default_url):
    """Return a safe internal redirect target or the fallback URL."""
    next_url = request.args.get('next') or request.form.get('next') or ''

    if not next_url:
        return default_url

    if next_url.startswith('http://') or next_url.startswith('https://'):
        return default_url

    if next_url.startswith('//'):
        return default_url

    if not next_url.startswith('/'):
        return default_url

    return next_url


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    next_target = _get_safe_next_url(url_for('dashboard.render_dashboard'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Register user
        success, message, user = register_user(full_name, email, password, confirm_password)
        
        if success:
            # Store user in session
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user_name'] = user.full_name
            session.permanent = request.form.get('remember_me') == 'on'
            
            flash(message, 'success')
            return redirect(next_target)
        else:
            flash(message, 'error')
    
    return render_template('auth/auth.html', next=next_target)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    next_target = _get_safe_next_url(url_for('dashboard.render_dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember_me = request.form.get('remember_me') == 'on'
        
        # Login user
        success, message, user = login_user(email, password)
        
        if success:
            # Store user in session
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user_name'] = user.full_name
            session.permanent = remember_me
            
            flash(message, 'success')
            return redirect(next_target)
        else:
            flash(message, 'error')
    
    return render_template('auth/auth.html', next=next_target)


@bp.route('/logout', methods=['POST'])
def logout():
    """Handle user logout."""
    user_id = session.get('user_id')
    
    if user_id:
        logout_user(user_id)
    
    # Clear session
    session.clear()
    
    flash('Logged out successfully', 'success')
    return redirect(url_for('home.render_home'))


def login_required(f):
    """Decorator to protect routes that require login."""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'warning')
            next_url = request.path
            if request.query_string:
                next_url = f"{next_url}?{request.query_string.decode()}"
            return redirect(url_for('auth.login', next=next_url))
        return f(*args, **kwargs)
    
    return decorated_function

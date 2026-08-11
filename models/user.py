"""User model for authentication and profile management."""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from database import db


class User(db.Model):
    """User model representing an authenticated user, backed by the `users` table."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    subscription_plan = db.Column(db.String(20), nullable=False, default='free')  # 'free', 'pro', 'enterprise'
    scans_left = db.Column(db.Integer, nullable=False, default=5)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    last_login = db.Column(db.DateTime, nullable=True)
    profile_picture = db.Column(db.String(255), nullable=True)

    def __init__(self, full_name=None, email=None, password_hash=None,
                 subscription_plan='free', scans_left=5, created_at=None,
                 last_login=None, profile_picture=None, **kwargs):
        super().__init__(
            full_name=full_name,
            email=email,
            password_hash=password_hash,
            subscription_plan=subscription_plan,
            scans_left=scans_left,
            created_at=created_at or datetime.now(),
            last_login=last_login,
            profile_picture=profile_picture,
            **kwargs
        )
        self.is_authenticated = False

    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """Check if provided password matches hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'subscription_plan': self.subscription_plan,
            'scans_left': self.scans_left,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'profile_picture': self.profile_picture,
        }

    def __repr__(self):
        return f'<User {self.email}>'

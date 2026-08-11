"""Resume model for the AI Resume Builder feature."""

import json
from datetime import datetime

from database import db


class Resume(db.Model):
    """A user-owned, editable resume draft backed by the `resumes` table."""

    __tablename__ = 'resumes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    title = db.Column(db.String(150), nullable=False, default='Untitled Resume')
    target_role = db.Column(db.String(150), nullable=True)
    template = db.Column(db.String(50), nullable=False, default='classic')

    # Structured resume content (personal info, summary, experience, education,
    # skills, section order) stored as JSON text for schema flexibility.
    content_json = db.Column(db.Text, nullable=False, default='{}')

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_content(self):
        """Return the parsed resume content dict, defaulting to empty on corruption."""
        try:
            return json.loads(self.content_json) if self.content_json else {}
        except (TypeError, ValueError):
            return {}

    def set_content(self, content):
        """Persist a resume content dict as JSON text."""
        self.content_json = json.dumps(content or {})

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'target_role': self.target_role,
            'template': self.template,
            'content': self.get_content(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<Resume {self.id} user={self.user_id} title={self.title!r}>'

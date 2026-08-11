"""Resume version snapshot model for the AI Resume Builder."""

import json
from datetime import datetime

from database import db


class ResumeVersion(db.Model):
    """A point-in-time snapshot of a user's resume for restore/version history."""

    __tablename__ = "resume_versions"

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    action = db.Column(db.String(50), nullable=False, default="manual_save")
    note = db.Column(db.String(255), nullable=True)

    title = db.Column(db.String(150), nullable=False)
    target_role = db.Column(db.String(150), nullable=True)
    template = db.Column(db.String(50), nullable=False)
    content_json = db.Column(db.Text, nullable=False, default="{}")

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def get_content(self):
        try:
            return json.loads(self.content_json) if self.content_json else {}
        except (TypeError, ValueError):
            return {}

    def set_content(self, content):
        self.content_json = json.dumps(content or {})

    def to_dict(self):
        return {
            "id": self.id,
            "resume_id": self.resume_id,
            "user_id": self.user_id,
            "action": self.action,
            "note": self.note,
            "title": self.title,
            "target_role": self.target_role,
            "template": self.template,
            "content": self.get_content(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<ResumeVersion {self.id} resume={self.resume_id} user={self.user_id}>"

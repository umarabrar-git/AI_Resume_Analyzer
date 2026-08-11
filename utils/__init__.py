"""Central import router for utils package.

This keeps feature-based module paths organized while exposing commonly used
helpers from a single place.
"""

try:
    from .ats import analyze_resume, extract_resume_text
except ImportError:
    # Handle missing PyMuPDF for development
    def analyze_resume(*args, **kwargs):
        return {"error": "PyMuPDF not installed"}
    def extract_resume_text(*args, **kwargs):
        return ""

from .dashboard import build_session_context, seed_dashboard_session
from .parsing import allowed_file

__all__ = [
    "allowed_file",
    "analyze_resume",
    "build_session_context",
    "extract_resume_text",
    "seed_dashboard_session",
]

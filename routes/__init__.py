from .analysis.route import bp as analysis_bp
from .assistant.route import bp as assistant_bp
from .auth import bp as auth_bp
from .dashboard.route import bp as dashboard_bp
from .home.route import bp as home_bp
from .reports.route import bp as reports_bp
from .resume_creation.route import bp as resume_creation_bp
from .settings.route import bp as settings_bp
from .upload.route import bp as upload_bp
from .api.route import bp as api_bp
from routes.features.route import features_bp
from .how_it_works.route import how_it_works_bp
from .pricing.route import pricing_bp
from .about.route import about_bp
from .faq.route import faq_bp
from .legal.route import legal_bp

ALL_BLUEPRINTS = (
    home_bp,
    auth_bp,
    dashboard_bp,
    features_bp,
    how_it_works_bp,
    pricing_bp,
    about_bp,
    faq_bp,
    legal_bp,
    analysis_bp,
    assistant_bp,
    resume_creation_bp,
    reports_bp,
    settings_bp,
    upload_bp,
    api_bp,
)

def register_routes(app):
    """Register every page/upload blueprint with the Flask app."""
    for blueprint in ALL_BLUEPRINTS:
        app.register_blueprint(blueprint)

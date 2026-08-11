from flask import Flask
from datetime import timedelta
from flask_session import Session

from config import Config
from database import init_db
from routes import register_routes
from services.resume_intelligence.agents import initialize_agent_service

# ======================================
# Create Flask Application
# ======================================

app = Flask(__name__)

# ======================================
# Load Configuration
# ======================================

app.config.from_object(Config)

# ======================================
# Session Configuration
# ======================================

app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize session
Session(app)

# ======================================
# Database Initialization
# ======================================

init_db(app)

initialize_agent_service()

register_routes(app)


# ======================================
# Run Flask Application
# ======================================

if __name__ == "__main__":
    app.run(debug=True)


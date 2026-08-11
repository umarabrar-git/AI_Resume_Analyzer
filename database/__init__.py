"""Database package: SQLAlchemy instance and initialization."""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect

db = SQLAlchemy()


def init_db(app):
    """Bind SQLAlchemy to the Flask app and create tables if they don't exist."""
    db.init_app(app)
    with app.app_context():
        # Import models here so they are registered with SQLAlchemy
        from models.user import User  # noqa: F401
        from models.resume import Resume  # noqa: F401
        from models.resume_version import ResumeVersion  # noqa: F401

        # Only create tables that are actually missing. Relying solely on
        # `create_all()`'s built-in checkfirst can raise "table already
        # exists" on Windows when the reloader restarts mid-request and the
        # dialect's table-existence check races with a stale connection.
        existing_tables = set(inspect(db.engine).get_table_names())
        missing_tables = [
            table for table in db.metadata.tables.values()
            if table.name not in existing_tables
        ]
        if missing_tables:
            db.metadata.create_all(bind=db.engine, tables=missing_tables)

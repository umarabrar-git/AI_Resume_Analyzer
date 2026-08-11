try:
    from .routes import bp
except ImportError:
    bp = None


__all__ = [
    "bp",
]
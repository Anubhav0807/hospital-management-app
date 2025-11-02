from flask_mail import Mail

mail = Mail()

from .auth import auth_bp

__all__ = ["auth_bp", "mail"]

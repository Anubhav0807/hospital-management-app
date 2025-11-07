from flask_mail import Mail

mail = Mail()

from .auth import auth_bp
from .admin import admin_bp
from .appointments import appointments_bp

__all__ = ["auth_bp", "admin_bp", "appointments_bp", "mail"]

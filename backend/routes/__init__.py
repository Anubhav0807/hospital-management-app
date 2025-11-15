from flask_caching import Cache
from flask_mail import Mail

cache = Cache()
mail = Mail()

from .base import base_bp
from .auth import auth_bp
from .admin import admin_bp
from .doctor import doctor_bp
from .patient import patient_bp
from .history import history_bp
from .analytics import analytics_bp

__all__ = [
  "base_bp", "auth_bp", "admin_bp",
  "doctor_bp", "patient_bp", "history_bp", "analytics_bp",
  "cache", "mail"
]

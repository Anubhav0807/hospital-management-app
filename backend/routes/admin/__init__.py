from flask import Blueprint

from .summary import summary_bp
from .manage_patients import manage_patients_bp
from .manage_doctors import manage_doctors_bp
from .appointments import appointments_bp

admin_bp = Blueprint("admin_bp", __name__, url_prefix="/api/admin")

# Register sub-blueprints
admin_bp.register_blueprint(summary_bp)
admin_bp.register_blueprint(manage_patients_bp)
admin_bp.register_blueprint(manage_doctors_bp)
admin_bp.register_blueprint(appointments_bp)

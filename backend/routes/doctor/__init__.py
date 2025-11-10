from flask import Blueprint

from .appointments import appointments_bp
from .patients import patients_bp
from .availability import availability_bp

doctor_bp = Blueprint("doctor_bp", __name__, url_prefix="/api/doctor")

# Register sub-blueprints
doctor_bp.register_blueprint(appointments_bp)
doctor_bp.register_blueprint(patients_bp)
doctor_bp.register_blueprint(availability_bp)

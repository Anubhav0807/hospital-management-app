from flask import Blueprint

from .summary import summary_bp
from .appointments import appointments_bp
from .doctors import doctors_bp 

patient_bp = Blueprint("patient_bp", __name__, url_prefix="/api/patient")

# Register sub-blueprints
patient_bp.register_blueprint(summary_bp)
patient_bp.register_blueprint(appointments_bp)
patient_bp.register_blueprint(doctors_bp)

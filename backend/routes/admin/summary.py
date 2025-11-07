from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from models import db, Doctor, Appointment, Patient

summary_bp = Blueprint("summary_bp", __name__)

@summary_bp.route("/summary", methods=["GET"])
@jwt_required()
def get_summary():
  claims = get_jwt()
  role = claims.get("role", "").lower()

  if role != "admin":
    return jsonify({"error": "Unauthorized: Admin access required"}), 403

  return jsonify({
    "patients": db.session.query(Patient).count(),
    "doctors": db.session.query(Doctor).count(),
    "appointments": db.session.query(Appointment).count()
  }), 200

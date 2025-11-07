from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy.exc import SQLAlchemyError
from models import db, User, Patient

manage_patients_bp = Blueprint("manage_patients_bp", __name__)

@manage_patients_bp.route("/patients", methods=["GET"])
@jwt_required()
def get_patients():
  claims = get_jwt()
  if claims.get("role", "").lower() != "admin":
    return jsonify({"error": "Unauthorized"}), 403

  patients = Patient.query.join(User).all()
  result = [
    {
      "id": p.user_id,
      "name": p.user.name,
      "age": p.age,
      "gender": p.gender.value if hasattr(p.gender, "value") else p.gender,
      "contact": p.user.contact_number,
      "address": p.address,
      "blacklisted": p.blacklisted
    }
    for p in patients
  ]
  return jsonify(result), 200

@manage_patients_bp.route("/patient/<int:patient_id>", methods=["DELETE"])
@jwt_required()
def delete_patient(patient_id):
  claims = get_jwt()
  if claims.get("role", "").lower() != "admin":
    return jsonify({"error": "Unauthorized"}), 403

  patient = Patient.query.get(patient_id)
  user = User.query.get(patient_id)
  if not patient or not user:
    return jsonify({"error": "Patient not found"}), 404

  try:
    db.session.delete(patient)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "Patient deleted successfully"}), 200

  except SQLAlchemyError as e:
    db.session.rollback()
    return jsonify({"error": str(e)}), 400

@manage_patients_bp.route("/patient/<int:patient_id>/blacklist", methods=["PATCH"])
@jwt_required()
def toggle_blacklist(patient_id):
  claims = get_jwt()
  if claims.get("role", "").lower() != "admin":
    return jsonify({"error": "Unauthorized"}), 403

  data = request.get_json()
  patient = Patient.query.get(patient_id)
  if not patient:
    return jsonify({"error": "Patient not found"}), 404

  patient.blacklisted = bool(data.get("blacklisted"))
  db.session.commit()

  return jsonify({"id": patient.user_id, "blacklisted": patient.blacklisted}), 200

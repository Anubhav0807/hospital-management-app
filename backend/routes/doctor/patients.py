from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime
from models import *

patients_bp = Blueprint("patients_bp", __name__)

@patients_bp.route("/patients", methods=["GET"])
@jwt_required()
def get_patients():
  claims = get_jwt()
  if claims.get("role", "").lower() not in ("admin", "doctor"):
    return jsonify({"error": "Unauthorized"}), 403

  user_id = get_jwt_identity()
  doctor = Doctor.query.filter_by(user_id=user_id).first()
  if not doctor:
    return jsonify({"error": "Doctor not found"}), 404

  patients = (
    Patient.query
    .join(Appointment, Appointment.patient_id == Patient.user_id)
    .filter(Appointment.doctor_id == doctor.user_id)
    .distinct()
    .all()
  )

  result = []
  for p in patients:
    last_appointment = (
      Appointment.query
      .filter_by(patient_id=p.user_id, doctor_id=doctor.user_id)
      .filter(Appointment.appointment_datetime < datetime.now())
      .order_by(Appointment.appointment_datetime.desc())
      .first()
    )

    result.append({
      "id": p.user_id,
      "name": p.user.name,
      "age": p.age,
      "gender": p.gender.value,
      "phone": p.user.contact_number,
      "email": p.user.email,
      "last_visit": last_appointment.appointment_datetime.isoformat() if last_appointment else None
    })

  return jsonify({"patients": result}), 200

@patients_bp.route("/patient/<int:patient_id>/history", methods=["GET"])
@jwt_required()
def get_patient_history(patient_id):
  claims = get_jwt()
  if claims.get("role", "").lower() not in ("admin", "doctor"):
    return jsonify({"error": "Unauthorized"}), 403

  appointments = (
    Appointment.query
    .filter_by(patient_id=patient_id)
    .order_by(Appointment.appointment_datetime.desc())
    .all()
  )

  if not appointments:
    return jsonify({"history": []}), 200

  history = [
    {
      "appointment_id": a.id,
      "date": a.appointment_datetime.isoformat(),
      "status": a.status.value,
    }
    for a in appointments
  ]

  patient = appointments[0].patient
  patient_data = {
    "id": patient.id,
    "name": patient.name,
    "age": patient.patient_profile.age,
    "gender": patient.patient_profile.gender.value,
    "phone": patient.contact_number,
  }

  return jsonify({"patient": patient_data, "history": history}), 200

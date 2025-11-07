from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from models import db, Appointment, StatusEnum

appointments_bp = Blueprint("appointments_bp", __name__, url_prefix="/api")

@appointments_bp.route("/appointments", methods=["GET"])
@jwt_required()
def get_appointments():
  claims = get_jwt()
  role = claims.get("role", "").lower()

  # Admin can view all
  if role == "admin":
    appts = Appointment.query.all()
  elif role == "doctor":
    doctor_id = claims.get("id")
    appts = Appointment.query.filter_by(doctor_id=doctor_id).all()
  elif role == "patient":
    patient_id = claims.get("id")
    appts = Appointment.query.filter_by(patient_id=patient_id).all()
  else:
    return jsonify({"error": "Unauthorized"}), 403

  result = []
  for appt in appts:
    result.append({
      "id": appt.id,
      "patient": appt.patient.name,
      "doctor": appt.doctor.name,
      "date": appt.appointment_datetime.strftime(r"%Y-%m-%d"),
      "time": appt.appointment_datetime.strftime(r"%I:%M %p"),
      "timestamp": int(appt.appointment_datetime.timestamp() * 1000),
      "status": appt.status.value
    })
  return jsonify({"appointments": result}), 200

@appointments_bp.route("/appointment/<int:appointment_id>", methods=["PUT"])
@jwt_required()
def update_appointment_status(appointment_id):
  data = request.get_json()
  status = data.get("status")

  if status not in StatusEnum._value2member_map_:
    return jsonify({"error": "Invalid status"}), 400
  
  claims = get_jwt()
  role = claims.get("role", "").lower()
  if role == "patient" and  status == StatusEnum.COMPLETED.value:
    return jsonify({"error": "Unauthorized"}), 403

  appt = Appointment.query.get_or_404(appointment_id)
  appt.status = StatusEnum(status)
  db.session.commit()

  return jsonify({"message": "Appointment updated successfully"}), 200

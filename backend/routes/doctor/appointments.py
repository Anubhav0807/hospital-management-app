from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime, timedelta
from models import *

appointments_bp = Blueprint("appointments_bp", __name__)

@appointments_bp.route("/appointments", methods=["GET"])
@jwt_required()
def get_appointments():
  claims = get_jwt()
  if claims.get("role", "").lower() not in ("admin", "doctor"):
    return jsonify({"error": "Unauthorized"}), 403

  user_id = get_jwt_identity()
  doctor = Doctor.query.filter_by(user_id=user_id).first()
  if not doctor:
    return jsonify({"error": "Doctor profile not found"}), 404

  days = int(request.args.get("days", "7"))
  now = datetime.now()
  end_time = now + timedelta(days=days)

  appointments = (
    Appointment.query
    .filter(Appointment.doctor_id == doctor.user_id)
    .filter(Appointment.appointment_datetime >= now)
    .filter(Appointment.appointment_datetime <= end_time)
    .order_by(Appointment.appointment_datetime.asc())
    .all()
  )

  result = [
    {
      "id": a.id,
      "patient_name": a.patient.name,
      "datetime": a.appointment_datetime.isoformat(),
      "status": a.status.value,
    }
    for a in appointments
  ]

  # Compute stats
  today_count = sum(1 for a in appointments if a.appointment_datetime.date() == now.date())
  completed_count = sum(1 for a in appointments if a.status == StatusEnum.COMPLETED)

  # Patient count (booked or completed only)
  active_patients = {
    a.patient_id
    for a in appointments
    if a.status in [StatusEnum.BOOKED, StatusEnum.COMPLETED]
  }
  patient_count = len(active_patients)

  return jsonify({
    "appointments": result,
    "today_count": today_count,
    "completed_count": completed_count,
    "patient_count": patient_count
  }), 200

@appointments_bp.route("/appointments/<int:appointment_id>", methods=["PATCH"])
@jwt_required()
def update_appointment_status(appointment_id):
  claims = get_jwt()
  if claims.get("role", "").lower() not in ("admin", "doctor"):
    return jsonify({"error": "Unauthorized"}), 403

  data = request.get_json() or {}
  status = StatusEnum(data.get("status"))

  if status not in [StatusEnum.COMPLETED, StatusEnum.CANCELLED]:
    return jsonify({"error": "Invalid status"}), 400

  appointment = Appointment.query.get_or_404(appointment_id)
  appointment.status = status
  db.session.commit()

  return jsonify({"message": f"Appointment marked as {status}."}), 200

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

@appointments_bp.route("/appointment/<int:appt_id>", methods=["PATCH"])
@jwt_required()
def cancel_appointment(appt_id):
  claims = get_jwt()
  if claims.get("role", "").lower() not in ("admin", "doctor"):
    return jsonify({"error": "Unauthorized"}), 403

  user_id = int(get_jwt_identity())
  appt = Appointment.query.get(appt_id)
  if not appt or appt.doctor_id != user_id:
    return jsonify({"error": "Appointment not found"}), 404

  appt.status = StatusEnum.CANCELLED
  db.session.commit()

  return jsonify({"message": "Appointment cancelled successfully"})

@appointments_bp.route("/treatment", methods=["POST"])
@jwt_required()
def create_treatment():
  data = request.get_json()
  appointment_id = data.get("appointment_id")
  visit_type = data.get("visit_type")
  diagnosis = data.get("diagnosis")
  test_done = data.get("test_done")
  prescription = data.get("prescription")
  notes = data.get("notes")

  appt = Appointment.query.get(appointment_id)
  if not appt:
    return jsonify({"error": "Appointment not found"}), 404

  treatment = Treatment(
    appointment_id=appointment_id,
    visit_type=VisitTypeEnum(visit_type),
    diagnosis=diagnosis,
    test_done=test_done,
    prescription=prescription,
    notes=notes,
  )
  appt.status = StatusEnum.COMPLETED

  db.session.add(treatment)
  db.session.commit()

  return jsonify({"message": "Treatment saved and appointment completed"})

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from models import db, User, Appointment, Availability, StatusEnum

appointments_bp = Blueprint("appointments_bp", __name__)

@appointments_bp.route("/appointments", methods=["GET"])
@jwt_required()
def get_appointments():
  user_id = int(get_jwt_identity())

  appointments = (
    Appointment.query
    .filter_by(patient_id=user_id)
    .order_by(Appointment.appointment_datetime)
    .all()
  )

  upcoming, past = [], []

  for a in appointments:
    item = {
      "id": a.id,
      "doctor": {
        "id": a.doctor.id,
        "name": a.doctor.name,
        "department": {
          "id": a.doctor.doctor_profile.department_id,
          "name": a.doctor.doctor_profile.department.name,
          "description": a.doctor.doctor_profile.department.description
        }
      },
      "date": a.appointment_datetime.isoformat(),
      "status": a.status.value,
      "diagnosis": a.treatment.diagnosis if a.treatment else None,
      "prescription": a.treatment.prescription if a.treatment else None
    }

    if a.status == StatusEnum.BOOKED:
      upcoming.append(item)
    elif a.status == StatusEnum.COMPLETED:
      past.append(item)

  return jsonify({"upcoming": upcoming, "past": past})

@appointments_bp.route("/appointments", methods=["POST"])
@jwt_required()
def book_appointment():
  user_id = int(get_jwt_identity())

  data = request.get_json()
  doctor_id = data.get("doctor_id")
  datetime_str = data.get("datetime")

  if not doctor_id or not datetime_str:
    return jsonify({"error": "Doctor and datetime are required"}), 400

  try:
    appt_datetime = datetime.fromisoformat(datetime_str)
  except ValueError:
    return jsonify({"error": "Invalid datetime format"}), 400

  doctor = User.query.filter_by(id=doctor_id).first()
  if not doctor or not doctor.is_doctor:
    return jsonify({"error": "Doctor not found"}), 404

  # Check doctor availability
  appt_date = appt_datetime.date()
  availability = Availability.query.filter_by(doctor_id=doctor_id, date=appt_date).first()
  if not availability or not availability.available:
    return jsonify({"error": "Doctor not available on that date"}), 409

  new_appt = Appointment(
    patient_id=user_id,
    doctor_id=doctor_id,
    appointment_datetime=appt_datetime,
    status=StatusEnum.BOOKED
  )

  db.session.add(new_appt)
  db.session.commit()

  return jsonify({
    "message": "Appointment booked successfully",
    "appointment_id": new_appt.id
  })

@appointments_bp.route("/appointment/<int:appt_id>", methods=["PUT"])
@jwt_required()
def reschedule_appointment(appt_id):
  user_id = int(get_jwt_identity())

  data = request.get_json()
  new_datetime = data.get("datetime")

  if not new_datetime:
    return jsonify({"error": "New datetime required"}), 400

  try:
    new_dt = datetime.fromisoformat(new_datetime)
  except ValueError:
    return jsonify({"error": "Invalid datetime format"}), 400

  appt = Appointment.query.get(appt_id)
  if not appt or appt.patient_id != user_id:
    print(appt.patient_id, user_id)
    return jsonify({"error": "Appointment not found"}), 404

  # Check doctor availability
  appt_date = new_dt.date()
  availability = Availability.query.filter_by(doctor_id=appt.doctor_id, date=appt_date).first()
  if not availability or not availability.available:
    return jsonify({"error": "Doctor not available on that date"}), 409

  # Update appointment
  appt.appointment_datetime = new_dt
  appt.status = StatusEnum.BOOKED
  db.session.commit()

  return jsonify({"message": "Appointment rescheduled successfully"})

@appointments_bp.route("/appointments/<int:appt_id>", methods=["DELETE"])
@jwt_required()
def cancel_appointment(appt_id):
  user_id = int(get_jwt_identity())

  appt = Appointment.query.get(appt_id)
  if not appt or appt.patient_id != user_id:
    return jsonify({"error": "Appointment not found"}), 404

  appt.status = StatusEnum.CANCELLED
  db.session.commit()

  return jsonify({"message": "Appointment cancelled successfully"})

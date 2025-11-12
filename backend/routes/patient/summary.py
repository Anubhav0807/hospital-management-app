from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Appointment, Treatment, StatusEnum

summary_bp = Blueprint("summary_bp", __name__)

@summary_bp.route("/summary", methods=["GET"])
@jwt_required()
def patient_summary():
  user_id = get_jwt_identity()
  user = User.query.get(user_id)

  if not user or not user.is_patient:
    return jsonify({"error": "Unauthorized"}), 403

  # Stats
  upcoming_count = Appointment.query.filter_by(patient_id=user_id, status=StatusEnum.BOOKED).count()
  visited_count = Appointment.query.filter_by(patient_id=user_id, status=StatusEnum.COMPLETED).count()
  prescriptions_count = Treatment.query.join(Appointment).filter(Appointment.patient_id == user_id).count()

  # Next appointment
  next_appt = (
    Appointment.query
    .filter(Appointment.patient_id == user_id, Appointment.status == StatusEnum.BOOKED)
    .order_by(Appointment.appointment_datetime.asc())
    .first()
  )

  # Recent diagnosis
  recent_treat = (
    Treatment.query
    .join(Appointment)
    .filter(Appointment.patient_id == user_id, Appointment.status == StatusEnum.COMPLETED)
    .order_by(Appointment.appointment_datetime.desc())
    .first()
  )

  recent_treatment = None
  if recent_treat:
    doctor = recent_treat.appointment.doctor
    recent_treatment = {
      "doctor": {
        "id": doctor.id,
        "name": doctor.name,
        "department": {
          "id": doctor.doctor_profile.department_id,
          "name": doctor.doctor_profile.department.name
        }
      },
      "diagnosis": recent_treat.diagnosis,
      "prescription": recent_treat.prescription,
      "date": recent_treat.appointment.appointment_datetime.isoformat(),
    }

  next_appointment = None
  if next_appt:
    next_appointment = {
      "id": next_appt.id,
      "doctor": {
        "id": next_appt.doctor.id,
        "name": next_appt.doctor.name,
        "department": {
          "id": next_appt.doctor.doctor_profile.department_id,
          "name": next_appt.doctor.doctor_profile.department.name,
          "description": next_appt.doctor.doctor_profile.department.description
        }
      },
      "date": next_appt.appointment_datetime.isoformat(),
      "status": next_appt.status.value
    }


  return jsonify({
    "user": {"id": user.id, "name": user.name},
    "stats": {
      "upcoming": upcoming_count,
      "visited": visited_count,
      "prescriptions": prescriptions_count
    },
    "next_appointment": next_appointment,
    "recent_diagnosis": recent_treatment
  })

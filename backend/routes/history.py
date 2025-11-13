from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Appointment, Treatment, RoleEnum

history_bp = Blueprint("history_bp", __name__, url_prefix="/api/history")


@history_bp.route("/treatments", methods=["GET"])
@jwt_required()
def get_treatments():
  user_id = get_jwt_identity()
  user = User.query.get(user_id)

  if not user:
    return jsonify({"error": "User not found"}), 404

  if user.role == RoleEnum.PATIENT:
    patient_id = user.id
  else:
    patient_id = request.args.get("patient_id", type=int)
    if not patient_id:
      return jsonify({"error": "patient_id is required"}), 400

  # Validate target is a patient
  target = User.query.get(patient_id)
  if not target or target.role != RoleEnum.PATIENT:
    return jsonify({"error": "Invalid patient_id"}), 404

  # Admin → access to all patients
  if user.role == RoleEnum.ADMIN:
    pass

  # Doctor → only if they have at least one appointment with that patient
  elif user.role == RoleEnum.DOCTOR:
    has_relation = Appointment.query.filter_by(
      doctor_id=user.id,
      patient_id=patient_id
    ).first()

    if not has_relation:
      return jsonify({
        "error": "Access denied. You have no appointments with this patient."
      }), 403

  # Patient → only allowed to view themselves (already ensured)
  elif user.role == RoleEnum.PATIENT:
    pass

  else:
    return jsonify({"error": "Invalid role"}), 403

  query = (
    db.session.query(Treatment, Appointment)
    .join(Appointment)
    .filter(Appointment.patient_id == patient_id)
    .order_by(Appointment.appointment_datetime.desc())
  )

  treatments = []
  for treatment, appointment in query.all():
    treatments.append({
      "id": treatment.id,
      "appointment_id": treatment.appointment_id,
      "date": appointment.appointment_datetime.isoformat(),
      "visit_type": treatment.visit_type.value,
      "diagnosis": treatment.diagnosis,
      "test_done": treatment.test_done,
      "prescription": treatment.prescription,
      "notes": treatment.notes
    })

  return jsonify({"treatments": treatments}), 200

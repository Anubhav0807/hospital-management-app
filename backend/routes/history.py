from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import db, User, Appointment, Treatment, RoleEnum
from tasks import export_treatment_history_csv

history_bp = Blueprint("history_bp", __name__, url_prefix="/api/history")

@history_bp.route("/treatments", methods=["GET"])
@jwt_required()
def get_treatments():
  user_id = get_jwt_identity()
  user = User.query.get(user_id)

  patient_id, error = resolve_patient_access(user, request)
  if error:
    return error  # <-- this returns (json, status_code)

  # Now patient_id is safe and validated
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

@history_bp.route("/export", methods=["POST"])
@jwt_required()
def export_history():
  user_id = get_jwt_identity()
  user = User.query.get(user_id)

  patient_id, error = resolve_patient_access(user, request)
  if error:
    return error

  export_treatment_history_csv.delay(patient_id, user_id)

  return jsonify({
    "message": "Export is being prepared. You will receive an email shortly."
  })

# Utility function
def resolve_patient_access(user, req):
  """
  Validates the current user's access and determines the patient_id.
  Returns:
    (patient_id, None) on success
    (None, (json_response, status_code)) on error
  """

  # User must exist
  if not user:
    return None, (jsonify({"error": "User not found"}), 404)

  # Determine patient_id based on role
  if user.role == RoleEnum.PATIENT:
    patient_id = user.id

  else:
    if request.method == "GET":
      patient_id = req.args.get("patient_id", type=int)
    elif request.method == "POST":
      patient_id = req.get_json().get("patient_id")
    else:
      return None, (jsonify({"error": "Unsupported request method"}), 400)
    
    if not patient_id:
      return None, (jsonify({"error": "patient_id is required"}), 400)

  # Validate target user exists and is a patient
  target = User.query.get(patient_id)
  if not target or target.role != RoleEnum.PATIENT:
    return None, (jsonify({"error": "Invalid patient_id"}), 404)

  # Admin: allowed for all patients
  if user.role == RoleEnum.ADMIN:
    return patient_id, None

  # Doctor: only allowed if they have an appointment with this patient
  if user.role == RoleEnum.DOCTOR:
    has_relation = Appointment.query.filter_by(
      doctor_id=user.id,
      patient_id=patient_id
    ).first()

    if not has_relation:
      return None, (
        jsonify({"error": "Access denied. You have no appointments with this patient."}),
        403
      )

    return patient_id, None

  # 6. Patient: only allowed to view themselves
  if user.role == RoleEnum.PATIENT:
    return patient_id, None

  # Fallback (unsupported role)
  return None, (jsonify({"error": "Invalid role"}), 403)

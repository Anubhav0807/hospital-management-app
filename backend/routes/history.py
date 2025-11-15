from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_
from datetime import datetime

from models import db, User, Appointment, Treatment, Role
from tasks import export_treatment_history_csv

history_bp = Blueprint("history_bp", __name__, url_prefix="/api/history")

@history_bp.route("/treatments", methods=["GET"])
@jwt_required()
def get_treatments():
  user_id = get_jwt_identity()
  user = User.query.get(user_id)

  patient_id, error = resolve_patient_access(user, request)
  if error:
    return error

  # Query parameters
  page = int(request.args.get("page", 1))
  per_page = int(request.args.get("per_page", 10))

  search = request.args.get("search", "").strip().lower()
  start_date = request.args.get("start_date")
  end_date = request.args.get("end_date")

  # Base query
  query = (
    db.session.query(Treatment, Appointment)
    .join(Appointment)
    .filter(Appointment.patient_id == patient_id)
  )

  # Date filtering
  if start_date:
    try:
      start = datetime.fromisoformat(start_date)
      query = query.filter(Appointment.appointment_datetime >= start)
    except:
      pass

  if end_date:
    try:
      end = datetime.fromisoformat(end_date)
      end = end.replace(hour=23, minute=59, second=59)
      query = query.filter(Appointment.appointment_datetime <= end)
    except:
      pass

  # Search filtering
  if search:
    query = query.filter(
      or_(
        Treatment.diagnosis.ilike(f"%{search}%"),
        Treatment.prescription.ilike(f"%{search}%"),
        Treatment.notes.ilike(f"%{search}%"),
        Treatment.test_done.ilike(f"%{search}%")
      )
    )

  # Total count before pagination
  total = query.count()

  # Pagination
  results = (
    query.order_by(Appointment.appointment_datetime.desc())
    .limit(per_page)
    .offset((page - 1) * per_page)
    .all()
  )

  # Build response
  records = []
  for treatment, appointment in results:
    records.append({
      "id": treatment.id,
      "appointment_id": treatment.appointment_id,
      "date": appointment.appointment_datetime.isoformat(),
      "visit_type": treatment.visit_type.value,
      "diagnosis": treatment.diagnosis,
      "test_done": treatment.test_done,
      "prescription": treatment.prescription,
      "notes": treatment.notes
    })

  return jsonify({
    "treatments": records,
    "total": total
  }), 200

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
  if user.role == Role.PATIENT:
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
  if not target or target.role != Role.PATIENT:
    return None, (jsonify({"error": "Invalid patient_id"}), 404)

  # Admin: allowed for all patients
  if user.role == Role.ADMIN:
    return patient_id, None

  # Doctor: only allowed if they have an appointment with this patient
  if user.role == Role.DOCTOR:
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
  if user.role == Role.PATIENT:
    return patient_id, None

  # Fallback (unsupported role)
  return None, (jsonify({"error": "Invalid role"}), 403)

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from datetime import date, datetime, timedelta

from models import User, Doctor, Department, Availability, Appointment, ApptStatus
from routes import cache

doctors_bp = Blueprint("doctors_bp", __name__)

# Helper function
def find_doctor_availability(doctor_id, days=7):
  today = date.today()
  end_date = today + timedelta(days=days)

  # Fetch doctor's availability for the next N days
  records = (
    Availability.query
    .filter_by(doctor_id=doctor_id)
    .filter(Availability.date >= today)
    .filter(Availability.date <= end_date)
    .order_by(Availability.date.asc())
    .all()
  )

  # Convert records to a dictionary for quick lookup
  availability_map = {a.date: a for a in records}

  result = []
  for i in range(days):
    current_date = today + timedelta(days=i)
    a = availability_map.get(current_date)

    if a:
      result.append({
        "date": a.date.isoformat(),
        "available": a.available,
        "start_time": a.start_time.strftime("%H:%M") if a.start_time else None,
        "end_time": a.end_time.strftime("%H:%M") if a.end_time else None,
      })
    else:
      # Fill missing days with default unavailable slots
      result.append({
        "date": current_date.isoformat(),
        "available": False,
        "start_time": None,
        "end_time": None,
      })

  return result

@doctors_bp.route("/doctors", methods=["GET"])
@jwt_required()
@cache.cached(timeout=300, query_string=True)
def get_doctors():
  department_id = request.args.get("department_id")

  if department_id:
    doctors = (
      Doctor.query
      .join(User)
      .filter(Doctor.department_id == department_id)
      .filter(Doctor.blacklisted == False)
      .all()
  )

  else:
    doctors = (
      Doctor.query
      .join(User)
      .filter(Doctor.blacklisted == False)
      .all()
    )

  result = []

  for d in doctors:
    result.append({
      "id": d.user_id,
      "name": d.user.name,
      "department": {
        "name": d.department.name,
        "description": d.department.description
      },
      "availability": find_doctor_availability(d.user_id)
    })

  return jsonify({"doctors": result})

@doctors_bp.route("/doctor-availability/<int:doctor_id>", methods=["GET"])
@jwt_required()
@cache.cached(timeout=60, query_string=True)
def get_doctor_availability(doctor_id):
  days = int(request.args.get("days", "7"))
  result = find_doctor_availability(doctor_id, days)

  return jsonify({"availability": result}), 200

@doctors_bp.route("/doctor-departments")
@jwt_required()
@cache.cached(timeout=600)
def get_departments():
  # Only include departments that have at least one doctor
  departments = (
    Department.query
    .join(Doctor)
    .filter(Doctor.blacklisted == False)
    .distinct()
    .all()
  )

  result = [
    {"id": d.id, "name": d.name, "description": d.description}
    for d in departments
  ]

  return jsonify({"departments": result}), 200

@doctors_bp.route("/doctor-bookings/<int:doctor_id>", methods=["GET"])
@jwt_required()
def get_doctor_bookings(doctor_id):
  start_date = request.args.get("start_date")
  end_date = request.args.get("end_date")

  try:
    if start_date:
      sd = datetime.fromisoformat(start_date).date()
    else:
      sd = None
    if end_date:
      ed = datetime.fromisoformat(end_date).date()
    else:
      ed = None
  except ValueError:
    return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400

  q = Appointment.query.filter(
    Appointment.doctor_id == doctor_id,
    Appointment.status == ApptStatus.BOOKED
  )

  if sd:
    q = q.filter(Appointment.appointment_datetime >= datetime.combine(sd, datetime.min.time()))
  if ed:
    q = q.filter(Appointment.appointment_datetime <= datetime.combine(ed, datetime.max.time()))

  appts = q.all()

  datetimes = [a.appointment_datetime.isoformat() for a in appts]

  return jsonify({"booked_datetimes": datetimes})

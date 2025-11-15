from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy import func
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from models import db, Appointment, Treatment, Doctor, Department

analytics_bp = Blueprint("analytics_bp", __name__, url_prefix="/api")

@analytics_bp.route("/analytics/charts", methods=["GET"])
@jwt_required()
def analytics_charts():
  claims = get_jwt()
  role = claims.get("role")
  user_id = claims.get("sub")

  if role == "admin":
    return jsonify(get_admin_analytics())

  elif role == "doctor":
    return jsonify(get_doctor_analytics(user_id))

  elif role == "patient":
    return jsonify(get_patient_analytics(user_id))

  return jsonify({"error": "Invalid role"}), 400


# ADMIN ANALYTICS
def get_admin_analytics():
  """System-wide analytics for admin."""

  # 1. Appointments Trend (Last 6 Months)
  six_months_ago = datetime.now() - timedelta(days=180)

  rows = (
    db.session.query(
      func.strftime('%Y-%m', Appointment.appointment_datetime).label("month"),
      func.count(Appointment.id)
    )
    .filter(Appointment.appointment_datetime >= six_months_ago)
    .group_by("month")
    .order_by("month")
    .all()
  )

  appointments_trend = {
    "labels": [
      datetime.strptime(r[0], "%Y-%m").strftime("%b %Y")
      for r in rows
    ],
    "values": [r[1] for r in rows],
    "label": "Appointments per Month"
  }

  # 2. Specialization Demand
  dept_rows = (
    db.session.query(
      Department.name,
      func.count(Appointment.id)
    )
    .join(Doctor, Doctor.department_id == Department.id)
    .join(Appointment, Appointment.doctor_id == Doctor.user_id)
    .group_by(Department.id)
    .order_by(Department.name)
    .all()
  )

  specialization_demand = {
    "labels": [r[0] for r in dept_rows],
    "values": [r[1] for r in dept_rows],
    "label": "Department Demand"
  }

  # 3. Visit Type Distribution
  type_rows = (
    db.session.query(
      Treatment.visit_type,
      func.count(Treatment.id)
    )
    .group_by(Treatment.visit_type)
    .all()
  )

  visit_type_dist = {
    "labels": [r[0].value.capitalize() for r in type_rows],
    "values": [r[1] for r in type_rows],
    "label": "Visit Types"
  }

  # 4. Patient Retention Trend (Last 6 Months)
  all_rows = (
    db.session.query(
      Appointment.patient_id,
      Appointment.appointment_datetime
    )
    .filter(Appointment.appointment_datetime >= six_months_ago)
    .order_by(Appointment.appointment_datetime)
    .all()
  )

  visits_by_patient = defaultdict(int)
  retention_by_month = defaultdict(lambda: {"new": 0, "returning": 0})

  for patient_id, dt in all_rows:
    month_key = dt.strftime("%Y-%m")
    visits_by_patient[patient_id] += 1

    if visits_by_patient[patient_id] == 1:
      retention_by_month[month_key]["new"] += 1
    else:
      retention_by_month[month_key]["returning"] += 1

  sorted_months = sorted(retention_by_month.keys())

  retention_trend = {
    "labels": [
      datetime.strptime(m, "%Y-%m").strftime("%b %Y")
      for m in sorted_months
    ],
    "values": [
      round(
        retention_by_month[m]["returning"] /
        max(1, retention_by_month[m]["new"] + retention_by_month[m]["returning"]) * 100,
        2
      )
      for m in sorted_months
    ],
    "label": "Retention %"
  }

  return {
    "appointments_trend": appointments_trend,
    "specialization_demand": specialization_demand,
    "visit_types": visit_type_dist,
    "retention_trend": retention_trend
  }

# DOCTOR ANALYTICS
def get_doctor_analytics(doctor_id):
  """Analytics visible to the doctor only for their appointments."""

  now = datetime.now()
  start_of_month = datetime(now.year, now.month, 1)

  # 1. Appointments This Month
  rows = (
    db.session.query(
      func.strftime('%Y-%m-%d', Appointment.appointment_datetime).label("day"),
      func.count(Appointment.id)
    )
    .filter(Appointment.doctor_id == doctor_id)
    .filter(Appointment.appointment_datetime >= start_of_month)
    .group_by("day")
    .order_by("day")
    .all()
  )

  monthly = {
    "labels": [
      datetime.strptime(r[0], "%Y-%m-%d").strftime("%d %b")
      for r in rows
    ],
    "values": [r[1] for r in rows],
    "label": "Appointments This Month"
  }

  # 2. Follow-Up Rate (New vs Returning Patients)

  # Fetch all appointments for this doctor
  app_rows = (
    db.session.query(
      Appointment.patient_id
    )
    .filter(Appointment.doctor_id == doctor_id)
    .order_by(Appointment.appointment_datetime)
    .all()
  )

  patient_counts = Counter([r[0] for r in app_rows])

  new_patients = sum(1 for c in patient_counts.values() if c == 1)
  returning_patients = sum(1 for c in patient_counts.values() if c >= 2)

  followup_rate = {
    "labels": ["Returning Patients", "New Patients"],
    "values": [returning_patients, new_patients],
    "label": "Follow-Up Rate"
  }

  return {
    "doctor_monthly": monthly,
    "followup_rate": followup_rate
  }

# PATIENT ANALYTICS
def get_patient_analytics(patient_id):
  """Provide patient frequency + department charts."""

  six_months_ago = datetime.now() - timedelta(days=180)

  # 1. Visit Frequency Trend
  freq_rows = (
    db.session.query(
      func.strftime('%Y-%m', Appointment.appointment_datetime).label("month"),
      func.count(Appointment.id)
    )
    .filter(Appointment.patient_id == patient_id)
    .filter(Appointment.appointment_datetime >= six_months_ago)
    .group_by("month")
    .order_by("month")
    .all()
  )

  visit_frequency = {
    "labels": [
      datetime.strptime(r[0], "%Y-%m").strftime("%b %Y")
      for r in freq_rows
    ],
    "values": [r[1] for r in freq_rows],
    "label": "Visits per Month"
  }

  # 2. Most Visited Departments
  dept_rows = (
    db.session.query(
      Department.name,
      func.count(Appointment.id)
    )
    .join(Doctor, Doctor.user_id == Appointment.doctor_id)
    .join(Department, Department.id == Doctor.department_id)
    .filter(Appointment.patient_id == patient_id)
    .group_by(Department.id)
    .order_by(Department.name)
    .all()
  )

  patient_departments = {
    "labels": [r[0] for r in dept_rows],
    "values": [r[1] for r in dept_rows],
    "label": "Visits per Department"
  }

  return {
    "patient_frequency": visit_frequency,
    "patient_departments": patient_departments
  }

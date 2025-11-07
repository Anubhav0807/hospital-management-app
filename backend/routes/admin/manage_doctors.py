from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from models import db, User, Doctor, Department, RoleEnum
import hashlib

manage_doctors_bp = Blueprint("manage_doctors_bp", __name__)

@manage_doctors_bp.route("/doctors", methods=["GET"])
@jwt_required()
def get_doctors():
  claims = get_jwt()
  if claims.get("role", "").lower() != "admin":
    return jsonify({"error": "Unauthorized"}), 403

  doctors = Doctor.query.join(User).join(Department).all()
  result = [
    {
      "id": d.user_id,
      "name": d.user.name,
      "email": d.user.email,
      "contact": d.user.contact_number,
      "department": {
        "id": d.department.id,
        "name": d.department.name
      },
      "experience": d.experience_years,
      "blacklisted": d.blacklisted
    }
    for d in doctors
  ]
  return jsonify({"doctors": result}), 200

@manage_doctors_bp.route("/doctor", methods=["POST"])
@jwt_required()
def add_doctor():
  claims = get_jwt()
  if claims.get("role", "").lower() != "admin":
    return jsonify({"error": "Unauthorized"}), 403

  data = request.get_json()
  required = ["email", "name", "contact", "department_id", "experience_years"]
  if not all(field in data and data[field] for field in required):
    return jsonify({"error": "Missing required fields"}), 400

  try:
    # 1. Create user
    password = (data["name"][:4] + data["contact"][-4:]).encode()
    hashed_pw = hashlib.sha256(password).hexdigest()
    new_user = User(
      email=data["email"],
      password=hashed_pw,
      name=data["name"],
      contact_number=data["contact"],
      role=RoleEnum.DOCTOR
    )
    db.session.add(new_user)
    db.session.flush()  # get new_user.id

    # 2. Create doctor profile
    new_doctor = Doctor(
      user_id=new_user.id,
      department_id=data["department_id"],
      experience_years=data["experience_years"],
      blacklisted=False
    )
    db.session.add(new_doctor)
    db.session.commit()

    return jsonify({"message": "Doctor added successfully"}), 201

  except IntegrityError:
    db.session.rollback()
    return jsonify({"error": "Email already exists"}), 400

  except SQLAlchemyError as e:
    db.session.rollback()
    return jsonify({"error": str(e)}), 400

@manage_doctors_bp.route("/doctor/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_doctor(user_id):
  claims = get_jwt()
  if claims.get("role", "").lower() != "admin":
    return jsonify({"error": "Unauthorized"}), 403

  data = request.get_json()

  doctor = Doctor.query.get(user_id)
  user = User.query.get(user_id)
  if not doctor or not user:
    return jsonify({"error": "Doctor not found"}), 404

  try:
    user.name = data.get("name", user.name)
    user.contact_number = data.get("contact", user.contact_number)

    doctor.department_id = data.get("department_id", doctor.department_id)
    doctor.experience_years = data.get("experience_years", doctor.experience_years)

    db.session.commit()
    return jsonify({"message": "Doctor updated successfully"}), 200

  except SQLAlchemyError as e:
    db.session.rollback()
    return jsonify({"error": str(e)}), 400

@manage_doctors_bp.route("/doctor/<int:doctor_id>", methods=["DELETE"])
@jwt_required()
def delete_doctor(doctor_id):
  claims = get_jwt()
  if claims.get("role", "").lower() != "admin":
    return jsonify({"error": "Unauthorized"}), 403

  doctor = Doctor.query.get(doctor_id)
  user = User.query.get(doctor_id)
  if not doctor or not user:
    return jsonify({"error": "Doctor not found"}), 404

  try:
    db.session.delete(doctor)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "Doctor deleted successfully"}), 200

  except SQLAlchemyError as e:
    db.session.rollback()
    return jsonify({"error": str(e)}), 400

@manage_doctors_bp.route("/doctor/<int:user_id>/blacklist", methods=["PATCH"])
@jwt_required()
def toggle_blacklist(user_id):
  claims = get_jwt()
  if claims.get("role", "").lower() != "admin":
    return jsonify({"error": "Unauthorized"}), 403

  doctor = Doctor.query.get(user_id)
  if not doctor:
    return jsonify({"error": "Doctor not found"}), 404

  data = request.get_json()
  doctor.blacklisted = data.get("blacklisted", not doctor.blacklisted)

  db.session.commit()
  return jsonify({"message": "Blacklist status updated"}), 200

@manage_doctors_bp.route("/departments", methods=["GET"])
@jwt_required()
def get_departments():
  claims = get_jwt()
  if claims.get("role", "").lower() != "admin":
    return jsonify({"error": "Unauthorized"}), 403

  departments = Department.query.all()
  result = [
    {"id": d.id, "name": d.name, "description": d.description}
    for d in departments
  ]
  return jsonify({"departments": result}), 200

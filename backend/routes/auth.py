from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import Blueprint, jsonify, render_template, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_mail import Message
from models import *
from . import mail
import datetime
import hashlib
import os

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/api/auth")

# Use your app secret key for consistency
serializer = URLSafeTimedSerializer(os.getenv("APP_SECRET"))

@auth_bp.route("/login", methods=["POST"])
def login():
  data = request.get_json()
  email = data.get("email")
  password = data.get("password")

  if not email or not password:
    return jsonify({"error": "Email and password are required"}), 400

  # Find user
  user = User.query.filter_by(email=email).first()
  if not user:
    return jsonify({"error": "Invalid email or password"}), 401

  # Verify password (SHA-256)
  hashed_pw = hashlib.sha256(password.encode()).hexdigest()
  if hashed_pw != user.password:
    return jsonify({"error": "Invalid email or password"}), 401

  # Generate JWT Token
  access_token = create_access_token(
    identity=str(user.id),
    additional_claims={"role": user.role.value}
  )

  return jsonify({
    "message": "Loggged in successfully",
    "access_token": access_token,
    "user": {
      "id": user.id,
      "name": user.name,
      "email": user.email,
      "role": user.role.value
    }
  }), 200

@auth_bp.route("/register", methods=["POST"])
def register_patient():
  data = request.get_json()

  required_fields = ["name", "email", "password", "contact_number", "age", "gender", "address"]
  if not all(field in data for field in required_fields):
    return jsonify({"error": "Missing required fields"}), 400

  email = data["email"].strip().lower()
  password = data["password"]
  name = data["name"].strip()
  contact_number = data["contact_number"]
  age = data["age"]
  gender = data["gender"].lower()
  address = data["address"]
  medical_history = data.get("medical_history", "")

  # Validate gender
  if gender not in ["male", "female", "other"]:
    return jsonify({"error": "Invalid gender value"}), 400

  # Check if email already exists
  if User.query.filter_by(email=email).first():
    return jsonify({"error": "Email already registered"}), 409

  # Hash password
  hashed_pw = hashlib.sha256(password.encode()).hexdigest()

  # Create User (role = PATIENT)
  new_user = User(
    email=email,
    password=hashed_pw,
    name=name,
    contact_number=contact_number,
    role=RoleEnum.PATIENT,
  )
  db.session.add(new_user)
  db.session.flush()  # Get new_user.id before commit

  # Create Patient profile
  patient_profile = Patient(
    user_id=new_user.id,
    age=age,
    gender=GenderEnum(gender),
    address=address,
    medical_history=medical_history
  )
  db.session.add(patient_profile)
  db.session.commit()

  # Generate JWT Token
  token = create_access_token(
    identity=str(new_user.id),
    additional_claims={"role": new_user.role.value}
  )

  return jsonify({
    "message": "Patient registered successfully",
    "access_token": token,
    "user": {
      "id": new_user.id,
      "name": new_user.name,
      "email": new_user.email,
      "role": new_user.role.value
    }
  }), 201

@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
  data = request.get_json()
  email = data.get("email")
  EXPIRES_DELTA = 15  # minutes

  if not email:
    return jsonify({"message": "Email is required"}), 400

  user = User.query.filter_by(email=email).first()
  if not user:
    return jsonify({"message": "No account found with that email."}), 404

  # Generate a one-time reset token valid for 15 minutes
  reset_token = serializer.dumps(email, salt="password-reset-salt")

  # Frontend reset link
  reset_link = f"http://localhost:5173/reset-password?token={reset_token}"

  # Build email message
  msg = Message("Password Reset Request", recipients=[email])
  msg.html = render_template(
    "reset_password.html",
    name=user.name,
    reset_link=reset_link,
    expires_delta=EXPIRES_DELTA,
    year=datetime.datetime.now().year,
  )

  try:
    mail.send(msg)
    return jsonify({"message": "Reset link sent to your email."}), 200
  except Exception as e:
    print("Email send failed:", e)
    return jsonify({"message": "Failed to send email."}), 500


@auth_bp.route("/update-password", methods=["POST"])
def update_password():
  data = request.get_json()
  token = data.get("token")
  new_password = data.get("new_password")

  if not token or not new_password:
    return jsonify({"error": "Missing token or new password"}), 400

  try:
    # Decode token (valid for 15 minutes)
    email = serializer.loads(token, salt="password-reset-salt", max_age=900)
  except SignatureExpired:
    return jsonify({"error": "The reset link has expired"}), 400
  except BadSignature:
    return jsonify({"error": "Invalid or tampered token"}), 400

  # Find user by decoded email
  user = User.query.filter_by(email=email).first()
  if not user:
    return jsonify({"error": "User not found"}), 404

  # Hash new password and update
  hashed_pw = hashlib.sha256(new_password.encode()).hexdigest()
  user.password = hashed_pw
  db.session.commit()

  return jsonify({"message": "Password updated successfully"}), 200

@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
  user_id = get_jwt_identity()
  user = User.query.filter_by(id=user_id).first()

  if not user:
    return jsonify({"error": "User not found"}), 404

  # Base user data
  user_data = {
    "id": user.id,
    "email": user.email,
    "name": user.name,
    "contact_number": user.contact_number,
    "role": user.role.value,
  }

  # Add role-specific details
  if user.role.value.lower() == "doctor":
    doctor = user.doctor_profile
    user_data["doctor_profile"] = {
      "department_id": doctor.department_id,
      "department_name": doctor.department.name,
      "experience_years": doctor.experience_years,
      "blacklisted": doctor.blacklisted,
    }

  elif user.role.value.lower() == "patient":
    patient = user.patient_profile
    user_data["patient_profile"] = {
      "age": patient.age,
      "gender": patient.gender.value,
      "address": patient.address,
      "medical_history": patient.medical_history,
      "blacklisted": patient.blacklisted,
    }

  return jsonify(user_data), 200

@auth_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
  user_id = get_jwt_identity()
  user = User.query.filter_by(id=user_id).first()

  if not user:
    return jsonify({"error": "User not found"}), 404

  data = request.get_json()

  # Update base user fields
  if "name" in data:
    user.name = data["name"]
  if "contact_number" in data:
    user.contact_number = data["contact_number"]

  # Doctor-specific updates
  if user.role.value.lower() == "doctor" and "doctor_profile" in data:
    doc_data = data["doctor_profile"]
    doc = user.doctor_profile
    if not doc:
      return jsonify({"error": "Doctor profile not found"}), 400

    if "experience_years" in doc_data:
      doc.experience_years = int(doc_data["experience_years"])
    if "department_id" in doc_data:
      doc.department_id = int(doc_data["department_id"])

  # Patient-specific updates
  if user.role.value.lower() == "patient" and "patient_profile" in data:
    pat_data = data["patient_profile"]
    pat = user.patient_profile
    if not pat:
      return jsonify({"error": "Patient profile not found"}), 400

    if "age" in pat_data:
      pat.age = int(pat_data["age"])
    if "gender" in pat_data:
      pat.gender = GenderEnum(pat_data["gender"])
    if "address" in pat_data:
      pat.address = pat_data["address"]
    if "medical_history" in pat_data:
      pat.medical_history = pat_data["medical_history"]

  db.session.commit()
  return jsonify({"message": "Profile updated successfully"}), 200

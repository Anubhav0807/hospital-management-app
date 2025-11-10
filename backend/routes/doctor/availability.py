from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime, timedelta
from models import *

availability_bp = Blueprint("availability_bp", __name__)

@availability_bp.route("/availability", methods=["GET", "PUT"])
@jwt_required()
def manage_availability():
  claims = get_jwt()
  if claims.get("role", "").lower() not in ("admin", "doctor"):
    return jsonify({"error": "Unauthorized"}), 403

  user_id = get_jwt_identity()
  doctor = Doctor.query.filter_by(user_id=user_id).first()
  if not doctor:
    return jsonify({"error": "Doctor not found"}), 404

  # GET: Fetch availability
  if request.method == "GET":
    days = int(request.args.get("days", "7"))
    today = datetime.now().date()
    end_date = today + timedelta(days=days)

    records = (
      Availability.query
      .filter_by(doctor_id=doctor.user_id)
      .filter(Availability.date >= today)
      .filter(Availability.date <= end_date)
      .order_by(Availability.date.asc())
      .all()
    )

    # Convert to dict for easy lookup
    existing = {a.date: a for a in records}

    # Always generate full 7-day structure
    result = []
    for i in range(days):
      current = today + timedelta(days=i)
      if current in existing:
        a = existing[current]
        result.append({
          "date": a.date.isoformat(),
          "available": a.available,
          "start_time": a.start_time.strftime("%H:%M") if a.start_time else None,
          "end_time": a.end_time.strftime("%H:%M") if a.end_time else None,
        })
      else:
        # Default for missing day
        result.append({
          "date": current.isoformat(),
          "available": False,
          "start_time": "09:00",
          "end_time": "17:00",
        })

    return jsonify({"availability": result}), 200


  # PUT: Update availability
  data = request.get_json() or {}
  days = data.get("availability", [])

  Availability.query.filter_by(doctor_id=doctor.user_id).delete()

  for d in days:
    new_avail = Availability(
      doctor_id=doctor.user_id,
      date=datetime.fromisoformat(d["date"]).date(),
      available=d.get("available", False),
      start_time=datetime.strptime(d["start_time"], "%H:%M").time()
      if d.get("start_time") else None,
      end_time=datetime.strptime(d["end_time"], "%H:%M").time()
      if d.get("end_time") else None,
    )
    db.session.add(new_avail)

  db.session.commit()
  return jsonify({"message": "Availability updated successfully."}), 200

from flask import Blueprint, jsonify

base_bp = Blueprint("base_bp", __name__)

@base_bp.route("/", methods=["GET"])
def health_check():
  return jsonify({
    "status": "ok",
    "service": "Hospital Management API",
    "api_base_url": "/api"
  })

@base_bp.route("/api", methods=["GET"])
def api_root():
  return jsonify({
    "api": "Hospital Management System",
    "version": "1.0",
    "endpoints": [
      "/api/auth/*",
      "/api/admin/*",
      "/api/doctor/*",
      "/api/patient/*",
      "/api/history/*",
      "/api/analytics/*"
    ]
  })

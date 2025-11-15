from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables
load_dotenv()

from models import *
from routes import *
import hashlib
import os

def create_app():
  # Initialize Flask app
  app = Flask(__name__)

  # Register Blueprints
  app.register_blueprint(auth_bp)
  app.register_blueprint(admin_bp)
  app.register_blueprint(doctor_bp)
  app.register_blueprint(patient_bp)
  app.register_blueprint(history_bp)

  # Configure Database
  database_url = os.getenv("DATABASE_URL")

  # Fallback to local SQLite if DATABASE_URL not set
  if not database_url:
    current_dir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(current_dir, "hospital.sqlite3")
    database_url = f"sqlite:///{db_path}"

  app.config["SQLALCHEMY_DATABASE_URI"] = database_url
  db.init_app(app)

  # Configure Mail
  app.config["MAIL_SERVER"] = "smtp.gmail.com"
  app.config["MAIL_PORT"] = 587
  app.config["MAIL_USE_TLS"] = True
  app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
  app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
  app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_USERNAME")
  mail.init_app(app)

  # Configure Cache
  app.config["CACHE_TYPE"] = "RedisCache"
  app.config["CACHE_REDIS_URL"] = os.getenv("REDIS_URL")
  cache.init_app(app)

  # Configure JWT
  app.config["JWT_SECRET_KEY"] = os.getenv("APP_SECRET") or "devsecret"
  app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)
  jwt = JWTManager(app)

  # Handle unauthorized access
  @jwt.unauthorized_loader
  def unauthorized_response(callback):
    return jsonify({"error": "Missing or invalid token"}), 401

  with app.app_context():
    db.create_all()

    if not User.query.filter_by(email="admin@gmail.com").first():
      # Admin should be registered by default
      password = "superuser"
      pwHash = hashlib.sha256(password.encode()).hexdigest()
      admin = User(
        email="admin@gmail.com",
        password=pwHash,
        name="admin",
        contact_number="+91 90000 90000",
        role=RoleEnum.ADMIN,
      )
      db.session.add(admin)
      db.session.commit()

      print("[Database and tables created]")

  CORS(app, supports_credentials=True)

  return app

if __name__ == "__main__":
  app = create_app()
  app.run(host="0.0.0.0", port=5000, debug=True)

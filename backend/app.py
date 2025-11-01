from flask import Flask
from dotenv import load_dotenv
from models import *
import hashlib
import os

# Load environmental variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET")

# Configure Database
database_url = os.getenv("DATABASE_URL")

# Fallback to local SQLite if DATABASE_URL not set
if not database_url:
  current_dir = os.path.abspath(os.path.dirname(__file__))
  db_path = os.path.join(current_dir, "hospital.sqlite3")
  database_url = f"sqlite:///{db_path}"

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
db.init_app(app)

with app.app_context():
  db.create_all()

  if not User.query.filter_by(email="admin@gmail.com").first():
    # Admin should be registered by default
    password = "superuser"
    pwHash = hashlib.sha256(password.encode()).hexdigest()
    admin = User(
      email="admin@gmail.com", password=pwHash,
      name="admin", contact_number="+91 90000 90000",
      role=RoleEnum.ADMIN,
    )
    db.session.add(admin)
    db.session.commit()

    print("[Database and tables created]")

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000, debug=True)

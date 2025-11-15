from . import db
import enum

class Role(enum.Enum):
  ADMIN = "admin"
  DOCTOR = "doctor"
  PATIENT = "patient"

class Gender(enum.Enum):
  MALE = "male"
  FEMALE = "female"
  OTHER = "other"

class User(db.Model):
  __tablename__ = "user"

  id = db.Column(db.Integer, autoincrement=True, primary_key=True)
  email = db.Column(db.String(64), unique=True, nullable=False)
  password = db.Column(db.String(128), nullable=False)
  name = db.Column(db.String(64), nullable=False)
  contact_number = db.Column(db.String(16), nullable=False)
  role = db.Column(db.Enum(Role), nullable=False)

  # Relationships (these profiles can be None)
  doctor_profile = db.relationship("Doctor", back_populates="user", uselist=False)
  patient_profile = db.relationship("Patient", back_populates="user", uselist=False)

  def __repr__(self):
    return f"<User {self.id} - {self.role.value}>"

  # Role helpers
  @property
  def is_admin(self):
    return self.role == Role.ADMIN

  @property
  def is_doctor(self):
    return self.role == Role.DOCTOR

  @property
  def is_patient(self):
    return self.role == Role.PATIENT

class Doctor(db.Model):
  __tablename__ = "doctor"

  user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
  department_id = db.Column(db.Integer, db.ForeignKey("department.id"), nullable=False)
  experience_years = db.Column(db.Integer, default=0, nullable=False)
  blacklisted = db.Column(db.Boolean, default=False, nullable=False)

  # Relationships
  user = db.relationship("User", back_populates="doctor_profile", uselist=False)
  department = db.relationship("Department", back_populates="doctors")
  availabilities = db.relationship("Availability", back_populates="doctor", cascade="all, delete-orphan")

class Patient(db.Model):
  __tablename__ = "patient"

  user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
  age = db.Column(db.Integer, nullable=False)
  gender = db.Column(db.Enum(Gender), nullable=False)
  address = db.Column(db.Text, nullable=False)
  blacklisted = db.Column(db.Boolean, default=False, nullable=False)

  # Relationships
  user = db.relationship("User", back_populates="patient_profile", uselist=False)

class Availability(db.Model):
  __tablename__ = "availability"

  id = db.Column(db.Integer, primary_key=True)
  doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.user_id"), nullable=False)
  date = db.Column(db.Date, nullable=False)
  available = db.Column(db.Boolean, default=False, nullable=False)
  start_time = db.Column(db.Time)
  end_time = db.Column(db.Time)

  doctor = db.relationship("Doctor", back_populates="availabilities")

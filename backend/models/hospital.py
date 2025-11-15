from . import db
import enum

class ApptStatus(enum.Enum):
  BOOKED = "booked"
  COMPLETED = "completed"
  CANCELLED = "cancelled"

class VisitType(enum.Enum):
  ONLINE = "online"
  OFFLINE = "offline"

class PaymentStatus(enum.Enum):
  PENDING = "pending"
  PAID = "paid"
  FAILED = "failed"
  REFUNDED = "refunded"

class Appointment(db.Model):
  __tablename__ = "appointment"
  id = db.Column(db.Integer, autoincrement=True, primary_key=True)
  patient_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
  doctor_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
  appointment_datetime = db.Column(db.DateTime, nullable=False)
  status = db.Column(db.Enum(ApptStatus), default=ApptStatus.BOOKED, nullable=False)

  # Relationships
  patient = db.relationship("User", foreign_keys=[patient_id], backref="appointments_as_patient")
  doctor = db.relationship("User", foreign_keys=[doctor_id], backref="appointments_as_doctor")
  treatment = db.relationship("Treatment", back_populates="appointment", uselist=False)

class Treatment(db.Model):
  __tablename__ = "treatment"
  id = db.Column(db.Integer, autoincrement=True, primary_key=True)
  appointment_id = db.Column(db.Integer, db.ForeignKey("appointment.id"), nullable=False)
  visit_type = db.Column(db.Enum(VisitType), nullable=False)
  diagnosis = db.Column(db.String(128), nullable=False)
  test_done = db.Column(db.String(128))
  prescription = db.Column(db.Text)
  notes = db.Column(db.Text)
  fee = db.Column(db.Numeric(10, 2), nullable=False)
  payment_token = db.Column(db.String(64), unique=True, nullable=True)
  payment_status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)

  # Relationships
  appointment = db.relationship("Appointment", back_populates="treatment")

class Department(db.Model):
  __tablename__ = "department"
  id = db.Column(db.Integer, autoincrement=True, primary_key=True)
  name = db.Column(db.String(64), unique=True, nullable=False)
  description = db.Column(db.Text)

  # Relationships
  doctors = db.relationship("Doctor", back_populates="department", lazy=True)

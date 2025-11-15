from flask import render_template
from flask_mail import Message
from celery import shared_task
from datetime import date, time, datetime
import os

from models import Appointment, User
from routes import mail

@shared_task
def send_daily_appointment_reminders():
  today = date.today()
  start = datetime.now()
  end = datetime.combine(today, time.max)

  # Fetch today's appointments
  appointments = Appointment.query.filter(
    Appointment.appointment_datetime.between(start, end)
  ).all()

  success_count = 0
  failure_count = 0
  errors = []

  for appt in appointments:
    patient = User.query.get(appt.patient_id)
    doctor = User.query.get(appt.doctor_id)

    try:
      msg = Message(
        subject="Appointment Reminder",
        sender=os.getenv("MAIL_USERNAME"),
        recipients=[patient.email],
        html=render_template(
          "daily_reminder.html",
          patient_name=patient.name,
          doctor_name=doctor.name,
          department_name=doctor.doctor_profile.department.name,
          appointment_time=appt.appointment_datetime.strftime("%I:%M %p"),
          year=today.year
        )
      )

      mail.send(msg)
      success_count += 1

    except Exception as e:
      # Log the error
      failure_count += 1
      errors.append(f"Failed to send to {patient.email} — {str(e)}")
      continue

  return {
    "success": success_count,
    "failed": failure_count,
    "errors": errors
  }

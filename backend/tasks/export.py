from datetime import datetime
from celery import shared_task
from flask_mail import Message
import csv
import io
import os

from models import db, User, Appointment, Treatment, RoleEnum
from routes import mail

@shared_task
def export_treatment_history_csv(patient_id, requester_id):
  """
  Generate a CSV of the patient's treatment history and email it.
  """
  patient = User.query.get(patient_id)
  requester = User.query.get(requester_id)

  # Fetch all treatments for the patient
  records = (
    db.session.query(Treatment, Appointment)
    .join(Appointment, Treatment.appointment_id == Appointment.id)
    .filter(Appointment.patient_id == patient_id)
    .order_by(Appointment.appointment_datetime.desc())
    .all()
  )

  # Create CSV in memory
  output = io.StringIO()
  writer = csv.writer(output)

  # HEADERS (exactly matching HistoryTab.vue)
  writer.writerow([
    "Date",
    "Visit Type",
    "Diagnosis",
    "Tests Done",
    "Prescription",
    "Notes"
  ])

  # ROWS (exactly matching HistoryTab.vue)
  for treatment, appointment in records:
    
    # Format date same as frontend (en-IN)
    dt = appointment.appointment_datetime
    formatted_date = dt.strftime("%d %b %Y")  # same as toLocaleDateString('en-IN')

    writer.writerow([
      formatted_date,
      treatment.visit_type.value.title(),
      treatment.diagnosis,
      treatment.test_done or "",
      treatment.prescription or "",
      treatment.notes or ""
    ])

  csv_bytes = output.getvalue().encode("utf-8")
  output.close()

  # Prepare email
  filename = f"treatment_history_{datetime.now().strftime('%Y_%m_%d')}.csv"

  if requester.role == RoleEnum.ADMIN:
    mail_subject = "Patient Treatment History Export"
    mail_body = (
      f"Dear Admin,\n\n"
      f"Treatment history export of Patient{patient_id} is attached as a CSV file.\n\n"
      "- Anubhav's Clinic"
    )
    filename = f"patient{patient_id}_" + filename

  elif requester.role == RoleEnum.DOCTOR:
    mail_subject = "Patient Treatment History Export"
    mail_body = (
      f"Dear Dr. {requester.name},\n\n"
      f"Treatment history export of Patient{patient_id} is attached as a CSV file.\n\n"
      "- Anubhav's Clinic"
    )
    filename = f"patient{patient_id}_" + filename

  elif requester.role == RoleEnum.PATIENT:
    mail_subject = "Your Treatment History Export"
    mail_body = (
      f"Dear {patient.name},\n\n"
      "Your treatment history export is attached as a CSV file.\n\n"
      "- Anubhav's Clinic"
    )

  try:
    msg = Message(
      subject=mail_subject,
      sender=os.getenv("MAIL_USERNAME"),
      recipients=[requester.email],
      body=mail_body
    )
    msg.attach(filename, "text/csv", csv_bytes)

    mail.send(msg)

  except Exception as e:
    return {"error": str(e)}

  return {"status": "Email sent"}

from flask import render_template
from flask_mail import Message
from celery import shared_task
from datetime import datetime, date, timedelta
from calendar import monthrange
import pdfkit
import shutil
import os

from models import db, User, Appointment
from routes import mail

@shared_task
def generate_monthly_doctor_reports():
  start_dt, end_dt, start_date = get_previous_month_range()
  doctor_ids = get_doctors_with_appointments(start_dt, end_dt)

  config = wkhtmltopdf_config()
  sent = 0
  errors = []

  for doc_id in doctor_ids:
    doctor = User.query.get(doc_id)
    if not doctor:
      continue

    appts = get_doctor_appointments(doc_id, start_dt, end_dt)
    rows, totals, diagnosis_summary = build_report_data(appts)
    html = render_report_html(start_date, doctor, rows, totals, diagnosis_summary)

    try:
      pdf_bytes = generate_pdf(html, config)
      email_pdf_report(doctor, pdf_bytes, start_date)
      sent += 1
    except Exception as e:
      errors.append(f"Doctor {doc_id}: {e}")

  return {
    "doctors_with_reports": len(doctor_ids),
    "emails_sent": sent,
    "errors": errors
  }


# UTILITIES

def wkhtmltopdf_config():
  path = shutil.which("wkhtmltopdf")
  if path:
    return pdfkit.configuration(wkhtmltopdf=path)
  for p in ("/usr/bin/wkhtmltopdf", "/usr/local/bin/wkhtmltopdf"):
    if os.path.exists(p):
      return pdfkit.configuration(wkhtmltopdf=p)
  return None

def format_dt(dt):
  try:
    return dt.strftime("%Y-%m-%d %I:%M %p")
  except Exception:
    return str(dt)

def get_previous_month_range():
  today = date.today()
  first_of_this_month = today.replace(day=1)
  last_month_end = first_of_this_month - timedelta(days=1)

  year = last_month_end.year
  month = last_month_end.month

  start_date = date(year, month, 1)
  end_day = monthrange(year, month)[1]
  end_date = date(year, month, end_day)

  start_dt = datetime.combine(start_date, datetime.min.time())
  end_dt = datetime.combine(end_date, datetime.max.time())

  return start_dt, end_dt, start_date

def get_doctors_with_appointments(start_dt, end_dt):
  doctor_rows = (
    db.session.query(Appointment.doctor_id)
    .filter(
      Appointment.appointment_datetime >= start_dt,
      Appointment.appointment_datetime <= end_dt
    )
    .distinct()
    .all()
  )
  return [r[0] for r in doctor_rows if r[0] is not None]

def get_doctor_appointments(doc_id, start_dt, end_dt):
  return (
    Appointment.query.filter(
      Appointment.doctor_id == doc_id,
      Appointment.appointment_datetime >= start_dt,
      Appointment.appointment_datetime <= end_dt
    )
    .order_by(Appointment.appointment_datetime.asc())
    .all()
  )

def build_report_data(appts):
  rows = []
  diagnoses = {}
  treatment_count = 0
  patient_ids = set()

  for a in appts:
    patient_name = a.patient.name

    if a.treatment:
      diagnosis = a.treatment.diagnosis
      test_done = a.treatment.test_done
      prescription = a.treatment.prescription
      notes = a.treatment.notes
    else:
      diagnosis = None
      test_done = None
      prescription = None
      notes = None

    if diagnosis:
      diagnoses[diagnosis] = diagnoses.get(diagnosis, 0) + 1

    if a.treatment:
      treatment_count += 1

    patient_ids.add(a.patient_id)

    rows.append({
      "patient_name": patient_name,
      "datetime_str": format_dt(a.appointment_datetime),
      "diagnosis": diagnosis,
      "test_done": test_done,
      "treatment": prescription,
      "notes": notes
    })

  totals = {
    "total_appointments": len(appts),
    "unique_patients": len(patient_ids),
    "treatments": treatment_count
  }

  diagnosis_summary = sorted(diagnoses.items(), key=lambda x: x[1], reverse=True)

  return rows, totals, diagnosis_summary

def render_report_html(start_date, doctor, rows, totals, diagnosis_summary):
  return render_template(
    "monthly_report.html",
    month_label=start_date.strftime("%B %Y"),
    generated_on=datetime.now().strftime("%Y-%m-%d %I:%M %p"),
    doctor_name=doctor.name,
    doctor_email=doctor.email,
    doctor_department=doctor.doctor_profile.department.name,
    appointments=rows,
    totals=totals,
    diagnosis_summary=diagnosis_summary,
    year=start_date.year
  )

def generate_pdf(html, config):
  try:
    if config:
      return pdfkit.from_string(html, False, configuration=config)
    return pdfkit.from_string(html, False)
  except Exception as e:
    raise RuntimeError(f"PDF generation failed: {e}")

def email_pdf_report(doctor, pdf_bytes, start_date):
  try:
    msg = Message(
      subject=f"Monthly Report — {start_date.strftime('%B %Y')}",
      sender=os.getenv("MAIL_USERNAME"),
      recipients=[doctor.email],
      body=(
        f"Dear Dr. {doctor.name},\n\n"
        f"Please find attached your monthly patient report for "
        f"{start_date.strftime('%B %Y')}.\n\n"
        f"- Anubhav's Clinic"
      )
    )

    filename = f"monthly_report_{doctor.id}_{start_date.strftime('%Y_%m')}.pdf"
    msg.attach(filename, "application/pdf", pdf_bytes)

    mail.send(msg)
  except Exception as e:
    raise RuntimeError(f"Email send failed: {e}")

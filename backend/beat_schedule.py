from celery.schedules import crontab

beat_schedule = {
  # DAILY reminder job (7:00 AM IST)
  "daily-reminder-job": {
    "task": "tasks.reminders.send_daily_appointment_reminders",
    "schedule": crontab(hour=7, minute=0),
  },

  # MONTHLY report generation job (1st of every month at 8:00 AM IST)
  "monthly-report-job": {
    "task": "tasks.reports.generate_monthly_doctor_reports",
    "schedule": crontab(day_of_month=1, hour=8, minute=0),
  },
}

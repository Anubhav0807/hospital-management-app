from celery import Celery
import os

def make_celery():
  # Import inside function to avoid circular imports
  from app import create_app

  # Create Flask app
  flask_app = create_app()

  # Create Celery app
  celery = Celery(
    "hospital_tasks",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2"),
    include=[
      "tasks.reminders",
      "tasks.reports",
    ]
  )

  # Celery config
  celery.conf.update(
    timezone="Asia/Kolkata",
    enable_utc=False,
  )

  # Wrap Celery tasks in Flask app context
  class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
      with flask_app.app_context():
        return self.run(*args, **kwargs)

  celery.Task = ContextTask

  # Load beat schedule if available
  try:
    from beat_schedule import beat_schedule
    celery.conf.beat_schedule = beat_schedule
  except Exception as e:
    print(f"[Celery] Could not load beat schedule: {e}")

  return celery

celery_app = make_celery()

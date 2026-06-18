from celery import Celery
from celery.schedules import crontab
from src.config import settings

celery_app = Celery(
    "domain",
    broker=settings.rabbit.url,
    backend="rpc://",
    include=[
        "src.tasks.email_sender",
        "src.tasks.payment_checker",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_send_sent_event=True,
    task_queues={
        "email_sender": {
            "exchange": "email_sender",
            "routing_key": "email_sender",
        },
        "payment": {
            "exchange": "payment",
            "routing_key": "payment",
        },
    },
    # Настройки для Beat
    beat_schedule={
        "check-payment-every-minute": {
            "task": "payment_checker",
            "schedule": crontab(minute="*"),
            "options": {"queue": "payment"},
        },
    },
    beat_max_loop_interval=30,
    beat_scheduler="celery.beat:PersistentScheduler",
)

if __name__ == "__main__":
    celery_app.start()

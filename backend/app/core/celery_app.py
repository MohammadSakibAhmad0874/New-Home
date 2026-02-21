import os

try:
    from celery import Celery
    from core.config import settings

    celery_app = Celery(
        "worker",
        broker=settings.RABBITMQ_URL,
        backend=settings.REDIS_URL
    )

    celery_app.conf.task_routes = {
        "worker.run_ai_analysis": "ai_queue",
        "worker.send_email_notification": "email_queue",
        "worker.process_video_feed": "video_queue",
        "worker.generate_report": "analytics_queue",
        "worker.test_celery": "default_queue",
    }

    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
    )
except Exception:
    # Celery/Redis not available — app runs without background tasks
    celery_app = None


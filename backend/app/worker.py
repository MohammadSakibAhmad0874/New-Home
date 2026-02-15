from core.celery_app import celery_app
from services import ai, email, video, analytics

celery = celery_app

@celery_app.task(acks_late=True)
def test_celery(word: str) -> str:
    return f"test task return {word}"

@celery_app.task(acks_late=True)
def run_ai_analysis(user_id: int):
    return ai.analyze_usage_pattern(user_id)

@celery_app.task(acks_late=True)
def send_email_notification(user_email: str):
    return email.send_welcome_email(user_email)

@celery_app.task(acks_late=True)
def process_video_feed(camera_id: str):
    return video.process_camera_feed(camera_id)

@celery_app.task(acks_late=True)
def generate_report(period: str):
    return analytics.generate_analytics_report(period)

# Future: Import specific service tasks here
# from services.ai import run_ai_job
# from services.video import process_video

from fastapi import APIRouter, HTTPException
from schemas.services import (
    AIAnalysisRequest, 
    EmailRequest, 
    VideoProcessRequest, 
    AnalyticsRequest
)

try:
    from worker import (
        run_ai_analysis, 
        send_email_notification, 
        process_video_feed, 
        generate_report
    )
    CELERY_AVAILABLE = True
except Exception:
    CELERY_AVAILABLE = False

router = APIRouter()

def _check_celery():
    if not CELERY_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="Background tasks unavailable — Redis/Celery not configured"
        )

@router.post("/ai/analyze", response_model=dict)
def trigger_ai_analysis(request: AIAnalysisRequest):
    _check_celery()
    task = run_ai_analysis.delay(request.user_id)
    return {"msg": "AI Analysis started", "task_id": str(task.id)}

@router.post("/notifications/email", response_model=dict)
def trigger_email(request: EmailRequest):
    _check_celery()
    task = send_email_notification.delay(request.email)
    return {"msg": "Email sending started", "task_id": str(task.id)}

@router.post("/video/process", response_model=dict)
def trigger_video_processing(request: VideoProcessRequest):
    _check_celery()
    task = process_video_feed.delay(request.camera_id)
    return {"msg": "Video processing started", "task_id": str(task.id)}

@router.post("/analytics/generate", response_model=dict)
def trigger_analytics(request: AnalyticsRequest):
    _check_celery()
    task = generate_report.delay(request.period)
    return {"msg": "Analytics generation started", "task_id": str(task.id)}


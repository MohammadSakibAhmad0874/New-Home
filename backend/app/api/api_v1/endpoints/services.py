from fastapi import APIRouter
from schemas.services import (
    AIAnalysisRequest, 
    EmailRequest, 
    VideoProcessRequest, 
    AnalyticsRequest
)
from worker import (
    run_ai_analysis, 
    send_email_notification, 
    process_video_feed, 
    generate_report
)

router = APIRouter()

@router.post("/ai/analyze", response_model=dict)
def trigger_ai_analysis(request: AIAnalysisRequest):
    """
    Trigger background AI analysis.
    """
    task = run_ai_analysis.delay(request.user_id)
    return {"msg": "AI Analysis started", "task_id": str(task.id)}

@router.post("/notifications/email", response_model=dict)
def trigger_email(request: EmailRequest):
    """
    Trigger background email.
    """
    task = send_email_notification.delay(request.email)
    return {"msg": "Email sending started", "task_id": str(task.id)}

@router.post("/video/process", response_model=dict)
def trigger_video_processing(request: VideoProcessRequest):
    """
    Trigger background video job.
    """
    task = process_video_feed.delay(request.camera_id)
    return {"msg": "Video processing started", "task_id": str(task.id)}

@router.post("/analytics/generate", response_model=dict)
def trigger_analytics(request: AnalyticsRequest):
    """
    Trigger background analytics report.
    """
    task = generate_report.delay(request.period)
    return {"msg": "Analytics generation started", "task_id": str(task.id)}

import sys
import os

# Add the app directory to sys.path to ensure imports work
sys.path.append(os.path.join(os.path.dirname(__file__), "../app"))

from core.celery_app import celery_app

def test_task_routes():
    """
    Verify that tasks are routed to the correct queues.
    """
    routes = celery_app.conf.task_routes
    
    expected_routes = {
        "worker.run_ai_analysis": "ai_queue",
        "worker.send_email_notification": "email_queue",
        "worker.process_video_feed": "video_queue",
        "worker.generate_report": "analytics_queue",
        "worker.test_celery": "default_queue",
    }
    
    errors = []
    
    print("🔍 Verifying Celery Task Routes...")
    
    for task_name, expected_queue in expected_routes.items():
        if task_name not in routes:
            errors.append(f"❌ Missing route for task: {task_name}")
            continue
            
        actual_queue = routes[task_name]
        if actual_queue != expected_queue:
            errors.append(f"❌ Incorrect queue for {task_name}. Expected: {expected_queue}, Got: {actual_queue}")
        else:
            print(f"✅ {task_name} -> {expected_queue}")
            
    if errors:
        print("\nErrors found:")
        for error in errors:
            print(error)
        sys.exit(1)
    else:
        print("\n✅ All routing rules verified successfully!")
        
if __name__ == "__main__":
    test_task_routes()

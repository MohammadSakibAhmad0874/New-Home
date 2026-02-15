import time

def process_camera_feed(camera_id: str):
    """
    Simulate video processing (IO bound + CPU checks).
    """
    print(f"[Video Job] Connecting to feed for Camera {camera_id}...")
    
    # Simulate handshake
    time.sleep(0.5)
    
    # Simulate frame processing loop
    frames_processed = 0
    for i in range(5):
        time.sleep(0.2) # Frame decoding time
        frames_processed += 1
        
    print(f"[Video Job] Feed processed. Motion detected in {frames_processed} frames.")
    
    return {
        "camera_id": camera_id, 
        "event": "motion", 
        "frames": frames_processed,
        "timestamp": time.time()
    }

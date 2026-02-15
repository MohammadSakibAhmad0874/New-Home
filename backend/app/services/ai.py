import time
import random

def analyze_usage_pattern(user_id: int):
    """
    Simulate a heavy AI analysis job (CPU bound).
    """
    print(f"[AI Engine] Starting analysis for User {user_id}...")
    
    # Simulate CPU-bound task (e.g., matrix multiplication)
    start_time = time.time()
    matrix_size = 300
    matrix_a = [[random.random() for _ in range(matrix_size)] for _ in range(matrix_size)]
    matrix_b = [[random.random() for _ in range(matrix_size)] for _ in range(matrix_size)]
    result = [[0 for _ in range(matrix_size)] for _ in range(matrix_size)]
    
    # Simple O(N^3) loop to burn CPU
    for i in range(len(matrix_a)):
        for j in range(len(matrix_b[0])):
            for k in range(len(matrix_b)):
                result[i][j] += matrix_a[i][k] * matrix_b[k][j]
                
    duration = time.time() - start_time
    print(f"[AI Engine] Analysis complete for User {user_id}. CPU Time: {duration:.2f}s")
    
    return {
        "user_id": user_id, 
        "status": "optimized", 
        "confidence_score": 0.98,
        "processing_time": f"{duration:.2f}s"
    }

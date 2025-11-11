"""
Embedding extraction optimized for MX330

Copyright (c) 2025 Tekly IT Solutions. All rights reserved.
"""
from insightface.app import FaceAnalysis
import os

def init_insightface(use_gpu=False, gpu_id=0, det_size=(320, 320)):
    """
    Initialize InsightFace with CPU mode (GPU disabled)
    
    Args:
        use_gpu: Enable GPU acceleration (currently disabled)
        gpu_id: GPU device ID (not used in CPU mode)
        det_size: Detection size (160x160 for CPU)
    """
    try:
        # CPU MODE (always used)
        print("📦 Loading InsightFace models (CPU mode - buffalo_s)...")
        app = FaceAnalysis(
            name='buffalo_s',  # Use smaller model for low memory
            allowed_modules=['detection', 'recognition'],
            providers=['CPUExecutionProvider']
        )
        
        app.prepare(ctx_id=-1, det_size=(160, 160))
        print("✅ InsightFace ready on CPU with buffalo_s model!")
        return app
            
    except Exception as e:
        print(f"❌ InsightFace initialization failed: {e}")
        raise


def check_cpu_status():
    """Check system CPU status (CPU mode replacement)"""
    try:
        import psutil
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        print(f"\n💻 CPU Status:")
        print(f"   CPU Usage: {cpu_percent}%")
        print(f"   Memory Total: {memory.total / (1024**3):.2f}GB")
        print(f"   Memory Used: {memory.used / (1024**3):.2f}GB")
        print(f"   Memory Available: {memory.available / (1024**3):.2f}GB")
        
        if memory.percent > 80:
            print("⚠️ WARNING: High memory usage! Consider:")
            print("   - Closing other applications")
            print("   - Reducing batch size for processing")
        
        return cpu_percent, memory.total, memory.used
    except:
        return None, None, None
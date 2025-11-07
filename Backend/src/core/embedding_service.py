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
        # GPU CODE DISABLED - Using CPU mode only
        # if use_gpu:
        #     print(f"🎮 NVIDIA GeForce MX330 Detected (2GB VRAM)")
        #     print(f"📦 Loading InsightFace models (GPU mode)...")
        #     print(f"🎯 Detection size: {det_size} (optimized for 2GB VRAM)")
        #     
        #     try:
        #         # Set environment variables for memory optimization
        #         os.environ['MXNET_GPU_MEM_POOL_TYPE'] = 'Round'
        #         os.environ['MXNET_GPU_MEM_POOL_ROUND_LINEAR_CUTOFF'] = '26'
        #         
        #         app = FaceAnalysis(
        #             allowed_modules=['detection', 'recognition'],
        #             providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
        #         )
        #         
        #         # Use GPU (ctx_id=0 for GPU, -1 for CPU)
        #         app.prepare(ctx_id=gpu_id, det_size=det_size)
        #         
        #         print(f"✅ InsightFace ready on MX330 GPU!")
        #         print(f"💡 VRAM Usage: ~500-800MB (Monitor with nvidia-smi)")
        #         print(f"💡 Expected Speed: 3-5x faster than CPU")
        #         return app
        #         
        #     except Exception as e:
        #         print(f"⚠️ GPU initialization failed: {e}")
        #         print("\n🔧 Troubleshooting for MX330:")
        #         print("   1. Ensure onnxruntime-gpu is installed")
        #         print("   2. Try: pip install mxnet-cu121")
        #         print("   3. Reduce detection_size to (160, 160)")
        #         print("\nFalling back to CPU mode...")
        #         use_gpu = False
        
        # CPU MODE (always used)
        print("📦 Loading InsightFace models (CPU mode)...")
        app = FaceAnalysis(
            allowed_modules=['detection', 'recognition'],
            providers=['CPUExecutionProvider']
        )
        
        app.prepare(ctx_id=-1, det_size=(160, 160))
        print("✅ InsightFace ready on CPU!")
        return app
            
    except Exception as e:
        print(f"❌ InsightFace initialization failed: {e}")
        raise

# GPU MEMORY CHECK DISABLED - Using CPU mode only
# def check_gpu_memory():
#     """Check available GPU memory"""
#     try:
#         import subprocess
#         result = subprocess.run(
#             ['nvidia-smi', '--query-gpu=memory.free,memory.used,memory.total', 
#              '--format=csv,noheader,nounits'],
#             capture_output=True, text=True, timeout=5
#         )
#         
#         if result.returncode == 0:
#             free, used, total = map(int, result.stdout.strip().split(','))
#             print(f"\n💾 GPU Memory Status:")
#             print(f"   Total: {total}MB")
#             print(f"   Used: {used}MB")
#             print(f"   Free: {free}MB")
#             print(f"   Available for model: ~{free-200}MB")
#             
#             if free < 500:
#                 print("⚠️ WARNING: Low GPU memory! Consider:")
#                 print("   - Closing other GPU applications")
#                 print("   - Reducing detection_size to (160, 160)")
#                 print("   - Using CPU mode instead")
#             
#             return free, used, total
#     except:
#         pass
#     
#     return None, None, None


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
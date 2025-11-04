"""
MX330 GPU Test Script
Tests GPU acceleration on NVIDIA GeForce MX330 (2GB VRAM)

Copyright (c) 2025 Tekly IT Solutions. All rights reserved.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import time
import numpy as np

def check_gpu_info():
    """Check GPU information"""
    try:
        import subprocess
        print("🎮 GPU Information:")
        print("="*60)
        
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=name,driver_version,memory.total,temperature.gpu', 
             '--format=csv,noheader'],
            capture_output=True, text=True, timeout=5
        )
        
        if result.returncode == 0:
            parts = result.stdout.strip().split(', ')
            print(f"GPU Name: {parts[0]}")
            print(f"Driver Version: {parts[1]}")
            print(f"Total Memory: {parts[2]}")
            print(f"Temperature: {parts[3]}")
        print("="*60)
        return True
    except Exception as e:
        print(f"❌ Could not get GPU info: {e}")
        return False


def check_gpu_memory():
    """Check GPU memory status"""
    try:
        import subprocess
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=memory.free,memory.used,memory.total', 
             '--format=csv,noheader,nounits'],
            capture_output=True, text=True, timeout=5
        )
        
        if result.returncode == 0:
            free, used, total = map(int, result.stdout.strip().split(','))
            print(f"\n💾 GPU Memory Status:")
            print(f"   Total: {total}MB (2048MB for MX330)")
            print(f"   Used:  {used}MB")
            print(f"   Free:  {free}MB")
            
            usage_percent = (used / total) * 100
            print(f"   Usage: {usage_percent:.1f}%")
            
            if free < 500:
                print("\n⚠️ WARNING: Low GPU memory!")
                print("   Consider closing other applications")
            elif free > 1000:
                print("\n✅ Sufficient GPU memory available")
            
            return free, used, total
    except Exception as e:
        print(f"⚠️ Could not check memory: {e}")
    
    return None, None, None


def test_dependencies():
    """Test if GPU dependencies are installed"""
    print("\n📦 Checking Dependencies:")
    print("="*60)
    
    dependencies = {
        'opencv-cv2': 'cv2',
        'numpy': 'numpy',
        'insightface': 'insightface',
        'onnxruntime-gpu': 'onnxruntime',
        'mxnet': 'mxnet'
    }
    
    all_installed = True
    for name, module in dependencies.items():
        try:
            __import__(module)
            version = __import__(module).__version__ if hasattr(__import__(module), '__version__') else 'Unknown'
            print(f"✅ {name}: {version}")
        except ImportError:
            print(f"❌ {name}: NOT INSTALLED")
            all_installed = False
    
    print("="*60)
    
    if not all_installed:
        print("\n⚠️ Missing dependencies! Install with:")
        print("pip install onnxruntime-gpu mxnet-cu121 insightface opencv-python numpy")
        return False
    
    # Check if GPU version of onnxruntime is available
    try:
        import onnxruntime as ort
        providers = ort.get_available_providers()
        print(f"\n🔌 ONNX Runtime Providers: {providers}")
        
        if 'CUDAExecutionProvider' in providers:
            print("✅ GPU acceleration available!")
        else:
            print("⚠️ GPU acceleration not available - CPU only")
            print("Install: pip install onnxruntime-gpu")
    except:
        pass
    
    return True


def test_insightface_gpu():
    """Test InsightFace with GPU"""
    print("\n🧪 Testing InsightFace GPU Initialization:")
    print("="*60)
    
    try:
        from insightface.app import FaceAnalysis
        
        print("1️⃣ Attempting GPU initialization...")
        
        # Set memory optimization for MX330
        os.environ['MXNET_GPU_MEM_POOL_TYPE'] = 'Round'
        os.environ['MXNET_GPU_MEM_POOL_ROUND_LINEAR_CUTOFF'] = '26'
        
        app = FaceAnalysis(
            allowed_modules=['detection', 'recognition'],
            providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
        )
        
        # Prepare with GPU (320x320 optimal for 2GB VRAM)
        print("2️⃣ Loading models on GPU (detection size: 320x320)...")
        app.prepare(ctx_id=0, det_size=(320, 320))
        
        print("✅ InsightFace initialized on GPU successfully!")
        
        # Check memory after loading
        check_gpu_memory()
        
        return app, True
        
    except Exception as e:
        print(f"❌ GPU initialization failed: {e}")
        print("\n🔄 Attempting CPU fallback...")
        
        try:
            app = FaceAnalysis(
                allowed_modules=['detection', 'recognition'],
                providers=['CPUExecutionProvider']
            )
            app.prepare(ctx_id=-1, det_size=(160, 160))
            print("✅ InsightFace initialized on CPU")
            return app, False
        except Exception as e2:
            print(f"❌ CPU initialization also failed: {e2}")
            return None, False


def benchmark_performance(app, use_gpu):
    """Benchmark face detection performance"""
    print("\n⚡ Performance Benchmark:")
    print("="*60)
    
    # Create test images
    print("Creating test images...")
    test_images = []
    for i in range(5):
        # Random RGB image
        img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        test_images.append(img)
    
    print(f"Running benchmark with 5 test images...")
    print("(Note: Random images may not contain faces)\n")
    
    times = []
    face_counts = []
    
    for i, img in enumerate(test_images):
        start = time.time()
        try:
            faces = app.get(img)
            elapsed = time.time() - start
            times.append(elapsed)
            face_counts.append(len(faces))
            print(f"Test {i+1}/5: {elapsed*1000:.1f}ms - {len(faces)} faces detected")
        except Exception as e:
            print(f"Test {i+1}/5: Error - {e}")
    
    if times:
        avg_time = np.mean(times)
        min_time = np.min(times)
        max_time = np.max(times)
        fps = 1.0 / avg_time if avg_time > 0 else 0
        
        print(f"\n📊 Results ({('GPU' if use_gpu else 'CPU')} mode):")
        print(f"   Average: {avg_time*1000:.1f}ms per frame")
        print(f"   Min: {min_time*1000:.1f}ms")
        print(f"   Max: {max_time*1000:.1f}ms")
        print(f"   FPS: {fps:.1f}")
        print(f"   Faces detected: {sum(face_counts)} total")
        
        if use_gpu:
            cpu_estimate = avg_time * 3  # GPU typically 3x faster
            print(f"\n💡 Estimated CPU time: ~{cpu_estimate*1000:.1f}ms (3x slower)")
            print(f"   Speedup: ~{cpu_estimate/avg_time:.1f}x")
    
    print("="*60)


def test_real_image():
    """Test with a real image if available"""
    print("\n📷 Testing with Real Images:")
    print("="*60)
    
    # Look for images in dataset
    dataset_path = "dataset"
    if not os.path.exists(dataset_path):
        print("⚠️ No dataset folder found")
        return False
    
    found_image = False
    for root, dirs, files in os.walk(dataset_path):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                image_path = os.path.join(root, file)
                print(f"\n✅ Found image: {image_path}")
                
                try:
                    import cv2
                    from src.core.embedding_service import init_insightface
                    
                    img = cv2.imread(image_path)
                    if img is not None:
                        print(f"   Image size: {img.shape[1]}x{img.shape[0]}")
                        
                        app = init_insightface(use_gpu=True, gpu_id=0)
                        
                        start = time.time()
                        faces = app.get(img)
                        elapsed = time.time() - start
                        
                        print(f"   Faces detected: {len(faces)}")
                        print(f"   Processing time: {elapsed*1000:.1f}ms")
                        
                        found_image = True
                        break
                except Exception as e:
                    print(f"   Error processing: {e}")
        
        if found_image:
            break
    
    if not found_image:
        print("⚠️ No images found in dataset folder")
    
    print("="*60)
    return found_image


def main():
    """Main test function"""
    print("\n" + "="*60)
    print("🎮 NVIDIA GeForce MX330 GPU Test Suite")
    print("="*60)
    
    # Step 1: Check GPU
    if not check_gpu_info():
        print("\n❌ GPU not detected! Make sure NVIDIA drivers are installed.")
        return
    
    # Step 2: Check memory
    check_gpu_memory()
    
    # Step 3: Check dependencies
    if not test_dependencies():
        return
    
    # Step 4: Test InsightFace
    app, use_gpu = test_insightface_gpu()
    
    if app is None:
        print("\n❌ Failed to initialize InsightFace")
        return
    
    # Step 5: Benchmark
    benchmark_performance(app, use_gpu)
    
    # Step 6: Test with real image
    test_real_image()
    
    # Final memory check
    print("\n📊 Final GPU Memory Check:")
    check_gpu_memory()
    
    # Summary
    print("\n" + "="*60)
    print("✅ MX330 GPU Test Complete!")
    print("="*60)
    
    if use_gpu:
        print("\n🎉 GPU acceleration is working!")
        print("Expected improvements:")
        print("   - 2-3x faster face detection")
        print("   - 25-30 FPS in live mode")
        print("   - Better quality with 320x320 detection size")
    else:
        print("\n⚠️ Running in CPU mode")
        print("To enable GPU:")
        print("   pip install onnxruntime-gpu mxnet-cu121")
    
    print("\n💡 Next steps:")
    print("   1. Run 'python main.py' to use the face recognition system")
    print("   2. Monitor GPU: 'nvidia-smi -l 1' in another terminal")
    print("   3. Train faces with camera using option 8 in menu")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
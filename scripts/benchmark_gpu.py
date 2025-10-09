"""Simple micro-benchmark: GPU vs CPU for InsightFace in this repo

Place this file in scripts/ and run it from the repo root.

It will:
- try to initialize InsightFace in GPU mode (if your environment supports it)
- run a small number of random-image inferences and measure times
- fall back to CPU and repeat

This is a quick way to confirm whether GPU mode is actually faster on your machine.
"""
import os
import sys
import time
import numpy as np
import traceback

# Ensure the repository root is on sys.path so `from src...` works when running this script
# When Python executes a script by filename, sys.path[0] is the script's directory (scripts/).
# Add the parent directory (repo root) so imports like `src.core...` resolve.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_THIS_DIR)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)


def run_benchmark(app, n_images=20):
    """Run n_images random inferences using provided InsightFace app.

    Returns: tuple(avg_ms, min_ms, max_ms, successes, times_list)
    """
    times = []
    successes = 0
    for i in range(n_images):
        # Create a random RGB image similar to webcam/frame size
        img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        try:
            start = time.time()
            faces = app.get(img)
            elapsed = (time.time() - start) * 1000.0
            times.append(elapsed)
            if faces:
                successes += 1
        except Exception as e:
            # store a sentinel large value so averages reflect failures
            print(f"   ❌ Inference error on frame {i}: {e}")
            times.append(None)

    valid_times = [t for t in times if t is not None]
    if not valid_times:
        return None, None, None, successes, times

    avg = float(np.mean(valid_times))
    mn = float(np.min(valid_times))
    mx = float(np.max(valid_times))
    return avg, mn, mx, successes, times


def try_init(use_gpu=True, gpu_id=0, det_size=(320, 320)):
    """Try to initialize the repo's init_insightface function.
    Returns (app, used_gpu_flag)
    """
    try:
        from src.core.embedding_service import init_insightface
    except Exception as e:
        print("❌ Could not import init_insightface:", e)
        traceback.print_exc()
        return None, False

    try:
        app = init_insightface(use_gpu=use_gpu, gpu_id=gpu_id, det_size=det_size)
        # If init succeeded and use_gpu was requested, assume GPU used unless app raised
        return app, use_gpu
    except Exception as e:
        print(f"⚠️ init_insightface(use_gpu={use_gpu}) failed: {e}")
        return None, False


def print_summary(mode_name, avg, mn, mx, successes, n_images):
    print('\n' + '='*60)
    print(f"Results for {mode_name}:")
    if avg is None:
        print("   ❌ No valid timings (all runs failed)")
    else:
        print(f"   Average: {avg:.1f} ms")
        print(f"   Min:     {mn:.1f} ms")
        print(f"   Max:     {mx:.1f} ms")
        fps = 1000.0 / avg if avg > 0 else 0.0
        print(f"   Approx FPS: {fps:.1f}")
        print(f"   Successful detections (faces returned): {successes}/{n_images}")
    print('='*60 + '\n')


def main():
    n_images = 20

    print('\n== Quick GPU vs CPU micro-benchmark for InsightFace ==')

    # First, try GPU init
    print('\n-> Trying GPU initialization (if available)')
    app_gpu, used_gpu = try_init(use_gpu=True, gpu_id=0, det_size=(320, 320))

    if app_gpu is not None and used_gpu:
        print('\nRunning benchmark on GPU...')
        avg_g, min_g, max_g, succ_g, times_g = run_benchmark(app_gpu, n_images=n_images)
        print_summary('GPU mode', avg_g, min_g, max_g, succ_g, n_images)
    else:
        print('\n⚠️ GPU init not available or failed — skipping GPU benchmark')
        avg_g = min_g = max_g = None

    # Now CPU fallback
    print('\n-> Initializing CPU mode (fallback)')
    app_cpu, _ = try_init(use_gpu=False, gpu_id=-1, det_size=(160, 160))
    if app_cpu is None:
        print('❌ CPU init failed too. Cannot benchmark.')
        return

    print('\nRunning benchmark on CPU...')
    avg_c, min_c, max_c, succ_c, times_c = run_benchmark(app_cpu, n_images=n_images)
    print_summary('CPU mode', avg_c, min_c, max_c, succ_c, n_images)

    # Compare if both succeeded
    if avg_g is not None and avg_c is not None:
        speedup = avg_c / avg_g if avg_g > 0 else float('inf')
        print(f"Summary: GPU avg {avg_g:.1f}ms vs CPU avg {avg_c:.1f}ms -> speedup ~{speedup:.2f}x")
    elif avg_g is None and avg_c is not None:
        print('Only CPU benchmark completed.')
    elif avg_g is not None and avg_c is None:
        print('Only GPU benchmark completed.')


if __name__ == '__main__':
    main()

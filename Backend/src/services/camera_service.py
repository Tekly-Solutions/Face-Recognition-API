"""Camera operations"""
import cv2

def init_camera(camera_id=0):
    """Initialize camera"""
    try:
        camera = cv2.VideoCapture(camera_id)
        if not camera.isOpened():
            print(f"❌ Could not open camera {camera_id}")
            return None
        
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        camera.set(cv2.CAP_PROP_FPS, 30)
        
        print(f"📷 Camera {camera_id} initialized successfully")
        return camera
    except Exception as e:
        print(f"❌ Camera initialization failed: {e}")
        return None

def close_camera(camera):
    """Close camera"""
    if camera:
        camera.release()
        cv2.destroyAllWindows()
        print("📷 Camera closed")
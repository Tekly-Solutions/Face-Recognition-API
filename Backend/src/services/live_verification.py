"""Live verification"""
import cv2
from datetime import datetime
from src.core.image_processor import process_frame_embedding
from src.services.verification_service import verify_embedding
from src.services.camera_service import init_camera

def capture_and_verify(app, camera, index, labels, threshold, save_image=True):
    """Capture image from camera and verify"""
    if camera is None:
        camera = init_camera()
        if camera is None:
            return None, 0.0, camera
    
    if index is None:
        print("❌ No face database loaded")
        return None, 0.0, camera
    
    print("📷 Starting camera capture...")
    print("Instructions:")
    print("- Position your face in the frame")
    print("- Press SPACE to capture")
    print("- Press ESC to cancel")
    
    captured = False
    captured_frame = None
    
    while True:
        ret, frame = camera.read()
        if not ret:
            print("❌ Failed to read from camera")
            break
        
        frame = cv2.flip(frame, 1)
        embedding, face_crop = process_frame_embedding(app, frame)
        
        cv2.putText(frame, "Press SPACE to capture, ESC to exit", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        if embedding is not None:
            label, score = verify_embedding(index, labels, embedding, threshold)
            if label:
                cv2.putText(frame, f"Detected: {label} ({score:.3f})", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.rectangle(frame, (10, 70), (200, 90), (0, 255, 0), 2)
            else:
                cv2.putText(frame, f"Unknown person ({score:.3f})", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.rectangle(frame, (10, 70), (200, 90), (0, 0, 255), 2)
        else:
            cv2.putText(frame, "No face detected", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        cv2.imshow('Face Verification - Capture Mode', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):
            captured_frame = frame.copy()
            captured = True
            break
        elif key == 27:
            break
    
    cv2.destroyAllWindows()
    
    if not captured:
        print("❌ Capture cancelled")
        return None, 0.0, camera
    
    print("📸 Image captured! Processing...")
    
    if save_image:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"captured_{timestamp}.jpg"
        cv2.imwrite(filename, captured_frame)
        print(f"💾 Image saved: {filename}")
    
    embedding, face_crop = process_frame_embedding(app, captured_frame)
    
    if embedding is None:
        print("❌ Could not process captured image")
        return None, 0.0, camera
    
    label, score = verify_embedding(index, labels, embedding, threshold)
    
    if label:
        print(f"✅ VERIFICATION SUCCESS: {label} (confidence: {score:.3f})")
    else:
        print(f"❌ VERIFICATION FAILED: Unknown person (score: {score:.3f})")
    
    return label, score, camera

def live_verification_mode(app, camera, index, labels, threshold):
    """Continuous live verification mode"""
    if camera is None:
        camera = init_camera()
        if camera is None:
            return camera
    
    if index is None:
        print("❌ No face database loaded")
        return camera
    
    print("🎥 Starting live verification mode...")
    print("Press ESC to exit")
    
    while True:
        ret, frame = camera.read()
        if not ret:
            print("❌ Failed to read from camera")
            break
        
        frame = cv2.flip(frame, 1)
        embedding, face_crop = process_frame_embedding(app, frame)
        
        cv2.putText(frame, "Live Face Verification (Press ESC to exit)", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        if embedding is not None:
            label, score = verify_embedding(index, labels, embedding, threshold)
            
            if label:
                cv2.putText(frame, f"VERIFIED: {label}", 
                           (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)
                cv2.putText(frame, f"Confidence: {score:.3f}", 
                           (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.rectangle(frame, (5, 5), (frame.shape[1]-5, frame.shape[0]-5), (0, 255, 0), 3)
            else:
                cv2.putText(frame, "UNKNOWN PERSON", 
                           (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
                cv2.putText(frame, f"Score: {score:.3f}", 
                           (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.rectangle(frame, (5, 5), (frame.shape[1]-5, frame.shape[0]-5), (0, 0, 255), 3)
        else:
            cv2.putText(frame, "No face detected", 
                       (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 3)
        
        cv2.imshow('Live Face Verification', frame)
        
        if cv2.waitKey(1) & 0xFF == 27:
            break
    
    cv2.destroyAllWindows()
    return camera
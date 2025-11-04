"""Training service for capturing and saving new faces"""
import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import cv2
from datetime import datetime
from src.services.camera_service import init_camera
from src.core.image_processor import process_frame_embedding

def capture_training_images(app, camera, person_name, num_images=5, dataset_path="dataset"):
    """
    Capture multiple images for training a new person
    
    Args:
        app: InsightFace application instance
        camera: Camera object (or None to initialize)
        person_name: Name of the person to train
        num_images: Number of images to capture (default: 5)
        dataset_path: Path to dataset directory
    
    Returns:
        Tuple of (success: bool, camera: object, captured_count: int)
    """
    if camera is None:
        camera = init_camera()
        if camera is None:
            return False, camera, 0
    
    # Convert to absolute path to ensure it's saved in the correct location
    if not os.path.isabs(dataset_path):
        dataset_path = os.path.abspath(dataset_path)
    
    print(f"📂 Dataset directory: {dataset_path}")
    
    # Create person folder
    person_folder = os.path.join(dataset_path, person_name)
    
    # Check if person already exists
    if os.path.exists(person_folder):
        print(f"⚠️  Person '{person_name}' already exists!")
        overwrite = input("Do you want to add more images? (y/n): ").lower().strip()
        if overwrite != 'y':
            return False, camera, 0
    else:
        os.makedirs(person_folder, exist_ok=True)
        print(f"📁 Created folder: {person_folder}")
    
    # Count existing images
    existing_images = len([f for f in os.listdir(person_folder) 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))])
    
    print(f"\n📷 TRAINING MODE: Capturing {num_images} images for '{person_name}'")
    print(f"Existing images: {existing_images}")
    print("\nInstructions:")
    print("- Position your face clearly in the frame")
    print("- Press SPACE to capture each image")
    print("- Try different angles and expressions")
    print("- Press ESC to cancel")
    print("="*60)
    
    captured_count = 0
    captured_images = []
    
    while captured_count < num_images:
        ret, frame = camera.read()
        if not ret:
            print("❌ Failed to read from camera")
            break
        
        frame = cv2.flip(frame, 1)
        
        # Check if face is detected
        embedding, face_crop = process_frame_embedding(app, frame)
        
        # Display instructions
        remaining = num_images - captured_count
        cv2.putText(frame, f"Capturing for: {person_name}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Images remaining: {remaining}", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        cv2.putText(frame, "Press SPACE to capture, ESC to cancel", 
                   (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Show face detection status
        if embedding is not None:
            cv2.putText(frame, "Face detected - Ready to capture!", 
                       (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.rectangle(frame, (5, 5), (frame.shape[1]-5, frame.shape[0]-5), (0, 255, 0), 3)
        else:
            cv2.putText(frame, "No face detected - Position your face", 
                       (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            cv2.rectangle(frame, (5, 5), (frame.shape[1]-5, frame.shape[0]-5), (0, 0, 255), 3)
        
        # Show captured images count
        if captured_count > 0:
            cv2.putText(frame, f"Captured: {captured_count}/{num_images}", 
                       (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        cv2.imshow('Training Mode - Capture Images', frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord(' '):  # Space key
            if embedding is None:
                print(f"❌ No face detected! Please position your face properly.")
                continue
            
            # Save the captured image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"training_{existing_images + captured_count + 1}_{timestamp}.jpg"
            image_path = os.path.join(person_folder, image_filename)
            
            cv2.imwrite(image_path, frame)
            captured_images.append(image_path)
            captured_count += 1
            
            print(f"✅ Captured {captured_count}/{num_images}: {image_filename}")
            
            # Visual feedback
            feedback_frame = frame.copy()
            cv2.putText(feedback_frame, f"CAPTURED! ({captured_count}/{num_images})", 
                       (frame.shape[1]//2 - 150, frame.shape[0]//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)
            cv2.imshow('Training Mode - Capture Images', feedback_frame)
            cv2.waitKey(500)  # Show feedback for 500ms
            
        elif key == 27:  # ESC key
            print("\n❌ Training cancelled by user")
            cv2.destroyAllWindows()
            return False, camera, captured_count
    
    cv2.destroyAllWindows()
    
    if captured_count == num_images:
        print(f"\n✅ Successfully captured {captured_count} images for '{person_name}'")
        print(f"📁 Saved to: {person_folder}")
        print("\n📋 Captured images:")
        for img_path in captured_images:
            print(f"   - {os.path.basename(img_path)}")
        return True, camera, captured_count
    else:
        print(f"\n⚠️  Only captured {captured_count}/{num_images} images")
        return False, camera, captured_count


def quick_train_face(app, camera, dataset_path="dataset"):
    """
    Quick training workflow: capture images and prompt to retrain model
    
    Args:
        app: InsightFace application instance
        camera: Camera object
        dataset_path: Path to dataset directory
    
    Returns:
        Tuple of (success: bool, camera: object, person_name: str)
    """
    print("\n" + "="*60)
    print("🎓 NEW FACE TRAINING")
    print("="*60)
    
    # Get person name
    person_name = input("\nEnter person's name: ").strip()
    
    if not person_name:
        print("❌ Name cannot be empty")
        return False, camera, None
    
    # Validate name (no special characters)
    if not person_name.replace(" ", "").replace("_", "").isalnum():
        print("❌ Name can only contain letters, numbers, spaces, and underscores")
        return False, camera, None
    
    # Replace spaces with underscores for folder name
    folder_name = person_name.replace(" ", "_")
    
    # Get number of images
    try:
        num_images = int(input("How many images to capture? (recommended: 5-10, default: 5): ").strip() or "5")
        if num_images < 1 or num_images > 20:
            print("⚠️  Number of images should be between 1 and 20. Using default (5)")
            num_images = 5
    except ValueError:
        print("⚠️  Invalid input. Using default (5 images)")
        num_images = 5
    
    # Capture images
    success, camera, captured_count = capture_training_images(
        app, camera, folder_name, num_images, dataset_path
    )
    
    if success:
        print("\n" + "="*60)
        print("✅ Training images captured successfully!")
        print("="*60)
        return True, camera, folder_name
    else:
        return False, camera, None
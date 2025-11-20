"""
FastAPI Server for Face Recognition System

Copyright (c) 2025 Tekly IT Solutions. All rights reserved.
PROPRIETARY SOFTWARE - Commercial use requires license agreement.
"""

import os
import sys
import base64
import cv2
import numpy as np
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Add current directory to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

from config.config import dataset_config
from src.core.embedding_service import init_insightface
from src.services.dataset_loader import load_dataset
from src.services.index_manager import build_index
from src.services.storage_service import save_model, load_model
from src.services.incremental_updater import incremental_update, full_rebuild_needed
from src.core.image_processor import process_single_image

# Initialize FastAPI app
app = FastAPI(
    title="Face Recognition API",
    description="Advanced face recognition system with training and verification",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class HealthResponse(BaseModel):
    status: str
    service: str
    faces_in_database: int
    system_initialized: bool

class TrainRequest(BaseModel):
    person_name: str
    images: List[str]

class VerifyRequest(BaseModel):
    image: str

class SaveEmployeePhotosRequest(BaseModel):
    employee_id: str
    first_name: str
    last_name: str
    photos: List[str]

class DatabaseInfo(BaseModel):
    total_faces: int
    unique_persons: int
    persons: List[str]
    person_image_counts: dict
    threshold: float

class TrainResponse(BaseModel):
    success: bool
    message: str
    person_name: str
    images_saved: int
    total_faces_in_database: int

class VerifyResponse(BaseModel):
    success: bool
    verified: bool
    person_name: Optional[str] = None
    confidence: Optional[float] = None
    threshold: float
    message: Optional[str] = None

class SaveEmployeePhotosResponse(BaseModel):
    success: bool
    message: str
    employee_id: str
    folder_name: str
    photos_saved: int
    saved_paths: List[str]

class FirebaseDownloadResponse(BaseModel):
    success: bool
    message: str
    images_downloaded: int
    total_faces_in_database: int
    persons_trained: List[str]

# Global variables
face_app = None
embeddings = []
labels = []
index = None
threshold = 0.6
dataset_path = dataset_config.dataset_path

def initialize_system():
    """Initialize face recognition system"""
    global face_app, embeddings, labels, index, threshold
    
    print("🚀 Initializing Face Recognition System...")
    
    # Initialize InsightFace
    face_app = init_insightface()
    
    # Auto-download images from Firebase
    print("\n☁️ Attempting to download images from Firebase Storage...")
    new_images_count, firebase_success = download_firebase_faces()
    
    # Load existing model or build if needed
    model_path = "models/enhanced_face_model.pkl"
    
    if os.path.exists(model_path):
        print("📁 Loading existing model...")
        embeddings, labels, threshold, index, success = load_model(model_path)
        if success:
            print(f"✅ Model loaded: {len(labels)} faces")
            
            # If new images from Firebase, do incremental update
            if new_images_count > 0:
                print("\n🔄 New images detected from Firebase. Performing incremental update...")
                embeddings, labels, index, changed = incremental_update(
                    face_app, dataset_path, embeddings, labels, index, threshold
                )
                if not changed:
                    print("✅ Model is already up to date with Firebase")
        else:
            print("⚠️ Failed to load model, doing full rebuild...")
            new_embeddings, new_labels, success = load_dataset(face_app, dataset_path)
            
            if success and len(new_embeddings) > 0:
                new_index = build_index(new_embeddings)
                if new_index:
                    save_model(new_embeddings, new_labels, threshold, new_index)
                    embeddings = new_embeddings
                    labels = new_labels
                    index = new_index
                    print(f"✅ Full model built: {len(labels)} faces in database")
                else:
                    print("⚠️ Failed to build index, starting fresh")
                    embeddings = []
                    labels = []
                    index = None
            else:
                print("⚠️ Failed to load dataset, starting fresh")
                embeddings = []
                labels = []
                index = None
    else:
        print("⚠️ No existing model found. Building initial model from dataset...")
        new_embeddings, new_labels, success = load_dataset(face_app, dataset_path)
        
        if success and len(new_embeddings) > 0:
            new_index = build_index(new_embeddings)
            if new_index:
                save_model(new_embeddings, new_labels, threshold, new_index)
                embeddings = new_embeddings
                labels = new_labels
                index = new_index
                print(f"✅ Initial model built: {len(labels)} faces in database")
            else:
                print("⚠️ Failed to build index, starting fresh")
                embeddings = []
                labels = []
                index = None
        else:
            print("⚠️ No dataset found, starting with empty model")
            embeddings = []
            labels = []
            index = None
    
    # Ensure dataset directory exists
    os.makedirs(dataset_path, exist_ok=True)
    
    print("✅ System initialized successfully")


def base64_to_image(base64_string: str):
    """Convert base64 string to OpenCV image"""
    try:
        # Remove data URI prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # Decode base64
        img_data = base64.b64decode(base64_string)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        return img
    except Exception as e:
        print(f"Error converting base64 to image: {e}")
        return None


def save_base64_image(base64_string: str, person_name: str, image_index: int):
    """Save base64 image to dataset folder"""
    try:
        img = base64_to_image(base64_string)
        if img is None:
            return None
        
        # Create person folder
        person_folder = os.path.join(dataset_path, person_name)
        os.makedirs(person_folder, exist_ok=True)
        
        # Save image with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"photo_{image_index}_{timestamp}.jpg"
        filepath = os.path.join(person_folder, filename)
        
        cv2.imwrite(filepath, img)
        print(f"✅ Saved: {filepath}")
        
        return filepath
    except Exception as e:
        print(f"Error saving image: {e}")
        return None

def download_firebase_faces():
    """Download all face images from Firebase Storage"""
    try:
        from src.services.firebase_downloader import download_all_faces
        
        print("\n☁️ Downloading faces from Firebase Storage...")
        new_images_count = download_all_faces(dataset_path)
        
        if new_images_count > 0:
            print(f"✅ Successfully downloaded {new_images_count} new images from Firebase")
            return new_images_count, True
        else:
            print("⚠️ No new images found in Firebase Storage")
            return 0, True
    except ImportError:
        print("⚠️ Firebase not configured - skipping Firebase download")
        return 0, True
    except Exception as e:
        print(f"❌ Firebase download error: {e}")
        return 0, False


@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    initialize_system()


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="Face Recognition API",
        faces_in_database=len(labels),
        system_initialized=face_app is not None
    )


@app.post("/save-employee-photos", response_model=SaveEmployeePhotosResponse)
async def save_employee_photos(request: SaveEmployeePhotosRequest):
    """
    Save employee photos to dataset without training
    
    Folder name format: FirstName_LastName_EmployeeID
    """
    try:
        employee_id = request.employee_id.strip()
        first_name = request.first_name.strip()
        last_name = request.last_name.strip()
        photos = request.photos
        
        # Validation
        if not employee_id:
            raise HTTPException(status_code=400, detail="employee_id is required")
        
        if not first_name or not last_name:
            raise HTTPException(status_code=400, detail="first_name and last_name are required")
        
        if not photos or len(photos) == 0:
            raise HTTPException(status_code=400, detail="photos array is required and must not be empty")
        
        # Create folder name: FirstName_LastName_EmployeeID
        folder_name = f"{first_name}_{last_name}_{employee_id}"
        
        # Sanitize folder name (remove special characters)
        folder_name = "".join(c if c.isalnum() or c == "_" else "_" for c in folder_name)
        
        print(f"\n📸 Saving photos for: {folder_name}")
        print(f"📊 Received {len(photos)} photos")
        
        # Save photos to dataset
        saved_photos = []
        for i, photo_base64 in enumerate(photos, 1):
            filepath = save_base64_image(photo_base64, folder_name, i)
            if filepath:
                saved_photos.append(filepath)
        
        if len(saved_photos) == 0:
            raise HTTPException(status_code=500, detail="Failed to save any photos")
        
        print(f"✅ Saved {len(saved_photos)} photos for {folder_name}")
        
        return SaveEmployeePhotosResponse(
            success=True,
            message=f"Successfully saved {len(saved_photos)} photos for {first_name} {last_name}",
            employee_id=employee_id,
            folder_name=folder_name,
            photos_saved=len(saved_photos),
            saved_paths=saved_photos
        )
            
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ Save photos error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/train", response_model=TrainResponse)
async def train_face(request: TrainRequest):
    """
    Train new face from base64 images and rebuild model
    """
    global embeddings, labels, index
    
    try:
        person_name = request.person_name.strip()
        images = request.images
        
        if not person_name:
            raise HTTPException(status_code=400, detail="person_name is required")
        
        if not images or len(images) == 0:
            raise HTTPException(status_code=400, detail="images array is required and must not be empty")
        
        # Validate and sanitize person name
        folder_name = person_name.replace(" ", "_")
        if not folder_name.replace("_", "").isalnum():
            raise HTTPException(status_code=400, detail="Invalid person_name. Use only letters, numbers, and spaces")
        
        print(f"\n📸 Training new face: {person_name}")
        print(f"📊 Received {len(images)} images")
        
        # Save images to dataset
        saved_images = []
        for i, img_base64 in enumerate(images, 1):
            filepath = save_base64_image(img_base64, folder_name, i)
            if filepath:
                saved_images.append(filepath)
        
        if len(saved_images) == 0:
            raise HTTPException(status_code=500, detail="Failed to save any images")
        
        print(f"✅ Saved {len(saved_images)} images")
        
        # Incremental update: Add only new person to model
        print("� Updating model incrementally...")
        new_embeddings, new_labels, new_index, model_changed = incremental_update(
            face_app, dataset_path, embeddings, labels, index, threshold
        )
        
        if new_index is not None:
            # Update global variables
            embeddings = new_embeddings
            labels = new_labels
            index = new_index
            
            print(f"✅ Model updated: {len(labels)} faces in database")
            
            return TrainResponse(
                success=True,
                message=f"Successfully trained face for {person_name}",
                person_name=person_name,
                images_saved=len(saved_images),
                total_faces_in_database=len(set(labels))
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to update model")
            
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ Training error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/verify", response_model=VerifyResponse)
async def verify_face(request: VerifyRequest):
    """
    Verify a face from base64 image
    """
    try:
        if index is None or len(labels) == 0:
            raise HTTPException(status_code=400, detail="No faces in database. Train faces first.")
        
        img_base64 = request.image
        
        # Convert base64 to image
        img = base64_to_image(img_base64)
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image data")
        
        # Save temp image
        temp_path = f"temp_verify_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        cv2.imwrite(temp_path, img)
        
        # Process image
        embedding = process_single_image(face_app, temp_path, "query")
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        if embedding is None:
            return VerifyResponse(
                success=False,
                verified=False,
                threshold=threshold,
                message="No face detected in image"
            )
        
        # Search in database
        D, I = index.search(np.array([embedding]).astype('float32'), k=1)
        top_score = float(D[0][0])
        top_label = labels[I[0][0]]
        
        if top_score >= threshold:
            return VerifyResponse(
                success=True,
                verified=True,
                person_name=top_label,
                confidence=round(top_score, 3),
                threshold=threshold
            )
        else:
            return VerifyResponse(
                success=True,
                verified=False,
                message="Unknown person",
                confidence=round(top_score, 3),
                threshold=threshold
            )
            
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ Verification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/database", response_model=DatabaseInfo)
async def get_database_info():
    """Get information about faces in database"""
    try:
        unique_labels = list(set(labels)) if len(labels) > 0 else []
        
        # Count images per person
        person_counts = {}
        if os.path.exists(dataset_path):
            for person_folder in os.listdir(dataset_path):
                person_path = os.path.join(dataset_path, person_folder)
                if os.path.isdir(person_path):
                    image_count = len([f for f in os.listdir(person_path) 
                                     if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))])
                    person_counts[person_folder] = image_count
        
        return DatabaseInfo(
            total_faces=len(labels),
            unique_persons=len(unique_labels),
            persons=unique_labels,
            person_image_counts=person_counts,
            threshold=threshold
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rebuild")
async def rebuild_model():
    """
    Incrementally update model with changes from Firebase
    
    This endpoint:
    - Adds new persons that were added to Firebase since last sync
    - Removes persons that were deleted from Firebase
    - Keeps existing embeddings for unchanged persons (no re-processing)
    """
    global embeddings, labels, index
    
    try:
        print("� Performing incremental model update...")
        
        # If model doesn't exist or is corrupted, do full rebuild
        if full_rebuild_needed(embeddings, labels, index):
            print("⚠️ Model corrupted or missing. Doing full rebuild...")
            new_embeddings, new_labels, success = load_dataset(face_app, dataset_path)
            
            if success and len(new_embeddings) > 0:
                new_index = build_index(new_embeddings)
                if new_index:
                    save_model(new_embeddings, new_labels, threshold, new_index)
                    
                    embeddings = new_embeddings
                    labels = new_labels
                    index = new_index
                    
                    return {
                        "success": True,
                        "message": "Full model rebuild completed",
                        "total_faces": len(labels),
                        "unique_persons": len(set(labels))
                    }
                else:
                    raise HTTPException(status_code=500, detail="Failed to build index")
            else:
                raise HTTPException(status_code=500, detail="No dataset found")
        
        # Incremental update
        new_embeddings, new_labels, new_index, model_changed = incremental_update(
            face_app, dataset_path, embeddings, labels, index, threshold
        )
        
        if new_index is not None:
            embeddings = new_embeddings
            labels = new_labels
            index = new_index
            
            return {
                "success": True,
                "message": "Incremental model update completed",
                "total_faces": len(labels),
                "unique_persons": len(set(labels)) if len(labels) > 0 else 0,
                "model_changed": model_changed
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to update model")
            
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/firebase/download", response_model=FirebaseDownloadResponse)
async def firebase_download():
    """
    Download all face images from Firebase Storage and update model incrementally
    
    This endpoint:
    1. Downloads new images from Firebase Storage (faces/ folder)
    2. Saves them to the local dataset folder
    3. Incrementally updates the model (adds new, removes missing)
    4. Returns updated database statistics
    """
    global embeddings, labels, index
    
    try:
        print("\n" + "="*60)
        print("📥 FIREBASE SYNC & INCREMENTAL MODEL UPDATE")
        print("="*60)
        
        # Download images from Firebase
        new_images_count, download_success = download_firebase_faces()
        
        if not download_success:
            raise HTTPException(
                status_code=500,
                detail="Failed to download images from Firebase"
            )
        
        # Perform incremental update
        print("\n🔄 Performing incremental model update...")
        
        # Handle case where model doesn't exist yet
        if full_rebuild_needed(embeddings, labels, index):
            print("⚠️ Model needs full rebuild. Building from scratch...")
            new_embeddings, new_labels, success = load_dataset(face_app, dataset_path)
            
            if success and len(new_embeddings) > 0:
                new_index = build_index(new_embeddings)
                if new_index:
                    save_model(new_embeddings, new_labels, threshold, new_index)
                    embeddings = new_embeddings
                    labels = new_labels
                    index = new_index
                else:
                    raise HTTPException(status_code=500, detail="Failed to build index")
            else:
                raise HTTPException(status_code=500, detail="No dataset found")
        else:
            # Incremental update
            new_embeddings, new_labels, new_index, model_changed = incremental_update(
                face_app, dataset_path, embeddings, labels, index, threshold
            )
            
            if new_index is not None:
                embeddings = new_embeddings
                labels = new_labels
                index = new_index
        
        unique_persons = list(set(labels)) if len(labels) > 0 else []
        
        print(f"\n✅ Sync & Update Complete")
        print(f"📊 Images downloaded: {new_images_count}")
        print(f"👥 Total faces in database: {len(labels)}")
        print(f"👤 Unique persons: {len(unique_persons)}")
        
        return FirebaseDownloadResponse(
            success=True,
            message=f"Successfully synced and updated model. Downloaded {new_images_count} new images." if new_images_count > 0 else "Model synced (no new images)",
            images_downloaded=new_images_count,
            total_faces_in_database=len(labels),
            persons_trained=unique_persons
        )
            
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ Firebase sync error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🚀 Face Recognition FastAPI Server")
    print("="*60)
    print("📍 API running on: http://0.0.0.0:8000")
    print("📖 Documentation: http://localhost:8000/docs")
    print("📖 Alternative Docs: http://localhost:8000/redoc")
    print("📊 Endpoints:")
    print("   GET  /health                  - Health check")
    print("   POST /save-employee-photos    - Save photos (no training)")
    print("   POST /train                   - Train face + rebuild model")
    print("   POST /verify                  - Verify face")
    print("   GET  /database                - Database info")
    print("   POST /rebuild                 - Rebuild model")
    print("   POST /firebase/download       - Download from Firebase & rebuild")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

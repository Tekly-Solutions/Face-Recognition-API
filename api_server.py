"""
Flask API Server for Face Recognition System

Copyright (c) 2025 Tekly IT Solutions. All rights reserved.
PROPRIETARY SOFTWARE - Commercial use requires license agreement.
"""

import os
import sys
import base64
import cv2
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
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
from src.services.training_service import capture_training_images
from src.core.image_processor import process_single_image

app = Flask(__name__)
CORS(app)

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
    
    # Load existing model if available
    model_path = "models/enhanced_face_model.pkl"
    if os.path.exists(model_path):
        print("📁 Loading existing model...")
        embeddings, labels, threshold, index, success = load_model(model_path)
        if success:
            print(f"✅ Model loaded: {len(labels)} faces")
        else:
            print("⚠️ Failed to load model, starting fresh")
            embeddings = []
            labels = []
            index = None
    else:
        print("⚠️ No existing model found")
    
    # Ensure dataset directory exists
    os.makedirs(dataset_path, exist_ok=True)
    
    print("✅ System initialized successfully")


def base64_to_image(base64_string):
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


def save_base64_image(base64_string, person_name, image_index):
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


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Face Recognition API',
        'faces_in_database': len(labels),
        'system_initialized': face_app is not None
    })


@app.route('/save-employee-photos', methods=['POST'])
def save_employee_photos():
    """
    Save employee photos to dataset without training
    
    Expected JSON:
    {
        "employee_id": "EMP001",
        "first_name": "John",
        "last_name": "Doe",
        "photos": ["base64_string_1", "base64_string_2", ...]
    }
    
    Folder name format: FirstName_LastName_EMP001
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        employee_id = data.get('employee_id', '').strip()
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        photos = data.get('photos', [])
        
        # Validation
        if not employee_id:
            return jsonify({'error': 'employee_id is required'}), 400
        
        if not first_name or not last_name:
            return jsonify({'error': 'first_name and last_name are required'}), 400
        
        if not photos or not isinstance(photos, list) or len(photos) == 0:
            return jsonify({'error': 'photos array is required and must not be empty'}), 400
        
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
            return jsonify({'error': 'Failed to save any photos'}), 500
        
        print(f"✅ Saved {len(saved_photos)} photos for {folder_name}")
        
        return jsonify({
            'success': True,
            'message': f'Successfully saved {len(saved_photos)} photos for {first_name} {last_name}',
            'employee_id': employee_id,
            'folder_name': folder_name,
            'photos_saved': len(saved_photos),
            'saved_paths': saved_photos
        }), 200
            
    except Exception as e:
        print(f"❌ Save photos error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/train', methods=['POST'])
def train_face():
    """
    Train new face from base64 images and rebuild model
    
    Expected JSON:
    {
        "person_name": "John Doe",
        "images": ["base64_string_1", "base64_string_2", ...]
    }
    """
    global embeddings, labels, index
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        person_name = data.get('person_name', '').strip()
        images = data.get('images', [])
        
        if not person_name:
            return jsonify({'error': 'person_name is required'}), 400
        
        if not images or not isinstance(images, list) or len(images) == 0:
            return jsonify({'error': 'images array is required and must not be empty'}), 400
        
        # Validate and sanitize person name
        folder_name = person_name.replace(" ", "_")
        if not folder_name.replace("_", "").isalnum():
            return jsonify({'error': 'Invalid person_name. Use only letters, numbers, and spaces'}), 400
        
        print(f"\n📸 Training new face: {person_name}")
        print(f"📊 Received {len(images)} images")
        
        # Save images to dataset
        saved_images = []
        for i, img_base64 in enumerate(images, 1):
            filepath = save_base64_image(img_base64, folder_name, i)
            if filepath:
                saved_images.append(filepath)
        
        if len(saved_images) == 0:
            return jsonify({'error': 'Failed to save any images'}), 500
        
        print(f"✅ Saved {len(saved_images)} images")
        
        # Rebuild model
        print("🔨 Rebuilding model...")
        new_embeddings, new_labels, success = load_dataset(face_app, dataset_path)
        
        if success and len(new_embeddings) > 0:
            new_index = build_index(new_embeddings)
            if new_index:
                save_model(new_embeddings, new_labels, threshold, new_index)
                
                # Update global variables
                embeddings = new_embeddings
                labels = new_labels
                index = new_index
                
                print(f"✅ Model rebuilt: {len(labels)} faces in database")
                
                return jsonify({
                    'success': True,
                    'message': f'Successfully trained face for {person_name}',
                    'person_name': person_name,
                    'images_saved': len(saved_images),
                    'total_faces_in_database': len(set(labels))
                }), 200
            else:
                return jsonify({'error': 'Failed to build index'}), 500
        else:
            return jsonify({'error': 'Failed to load dataset'}), 500
            
    except Exception as e:
        print(f"❌ Training error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/verify', methods=['POST'])
def verify_face():
    """
    Verify a face from base64 image
    
    Expected JSON:
    {
        "image": "base64_string"
    }
    """
    try:
        if index is None or len(labels) == 0:
            return jsonify({'error': 'No faces in database. Train faces first.'}), 400
        
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({'error': 'image is required'}), 400
        
        img_base64 = data['image']
        
        # Convert base64 to image
        img = base64_to_image(img_base64)
        if img is None:
            return jsonify({'error': 'Invalid image data'}), 400
        
        # Save temp image
        temp_path = f"temp_verify_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        cv2.imwrite(temp_path, img)
        
        # Process image
        embedding = process_single_image(face_app, temp_path, "query")
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        if embedding is None:
            return jsonify({
                'success': False,
                'message': 'No face detected in image'
            }), 200
        
        # Search in database
        D, I = index.search(np.array([embedding]).astype('float32'), k=1)
        top_score = float(D[0][0])
        top_label = labels[I[0][0]]
        
        if top_score >= threshold:
            return jsonify({
                'success': True,
                'verified': True,
                'person_name': top_label,
                'confidence': round(top_score, 3),
                'threshold': threshold
            }), 200
        else:
            return jsonify({
                'success': True,
                'verified': False,
                'message': 'Unknown person',
                'confidence': round(top_score, 3),
                'threshold': threshold
            }), 200
            
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/database', methods=['GET'])
def get_database_info():
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
        
        return jsonify({
            'total_faces': len(labels),
            'unique_persons': len(unique_labels),
            'persons': unique_labels,
            'person_image_counts': person_counts,
            'threshold': threshold
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/rebuild', methods=['POST'])
def rebuild_model():
    """Rebuild model from dataset"""
    global embeddings, labels, index
    
    try:
        print("🔨 Rebuilding model from dataset...")
        
        new_embeddings, new_labels, success = load_dataset(face_app, dataset_path)
        
        if success and len(new_embeddings) > 0:
            new_index = build_index(new_embeddings)
            if new_index:
                save_model(new_embeddings, new_labels, threshold, new_index)
                
                embeddings = new_embeddings
                labels = new_labels
                index = new_index
                
                return jsonify({
                    'success': True,
                    'message': 'Model rebuilt successfully',
                    'total_faces': len(labels),
                    'unique_persons': len(set(labels))
                }), 200
            else:
                return jsonify({'error': 'Failed to build index'}), 500
        else:
            return jsonify({'error': 'No dataset found or failed to load'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Initialize system on startup
    initialize_system()
    
    # Run Flask server
    print("\n" + "="*60)
    print("🚀 Face Recognition API Server")
    print("="*60)
    print("📍 API running on: http://localhost:8000")
    print("📖 Endpoints:")
    print("   GET  /health                  - Health check")
    print("   POST /save-employee-photos    - Save photos (no training)")
    print("   POST /train                   - Train face + rebuild model")
    print("   POST /verify                  - Verify face")
    print("   GET  /database                - Database info")
    print("   POST /rebuild                 - Rebuild model")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=8000, debug=True)
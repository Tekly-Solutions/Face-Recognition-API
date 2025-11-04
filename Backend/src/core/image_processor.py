"""Image processing"""
import os
import cv2
import numpy as np
from retinaface import RetinaFace
from src.core.face_detector import extract_face_from_retinaface

def process_single_image(app, image_path, class_name):
    """Process single image using the proven diagnostic method"""
    try:
        img = cv2.imread(image_path)
        if img is None:
            print(f"   ❌ Could not load: {os.path.basename(image_path)}")
            return None
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        try:
            faces = RetinaFace.detect_faces(img_rgb)
            if not isinstance(faces, dict) or len(faces) == 0:
                print(f"   ❌ No faces detected: {os.path.basename(image_path)}")
                return None
            
            face_crop = extract_face_from_retinaface(img_rgb, faces)
            if face_crop is None:
                print(f"   ❌ Could not extract face: {os.path.basename(image_path)}")
                return None
            
        except Exception as e:
            print(f"   ❌ RetinaFace error: {os.path.basename(image_path)} - {e}")
            return None
        
        try:
            face_bgr = cv2.cvtColor(face_crop, cv2.COLOR_RGB2BGR)
            insight_faces = app.get(face_bgr)
            
            if not insight_faces:
                print(f"   ❌ No embedding: {os.path.basename(image_path)}")
                return None
            
            face = insight_faces[0]
            embedding = face.embedding.astype('float32')
            embedding = embedding / np.linalg.norm(embedding)
            
            print(f"   ✅ Success: {os.path.basename(image_path)}")
            return embedding
            
        except Exception as e:
            print(f"   ❌ InsightFace error: {os.path.basename(image_path)} - {e}")
            return None
            
    except Exception as e:
        print(f"   ❌ General error: {os.path.basename(image_path)} - {e}")
        return None

def process_frame_embedding(app, frame):
    """Process a camera frame and return embedding"""
    try:
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        faces = RetinaFace.detect_faces(img_rgb)
        if not isinstance(faces, dict) or len(faces) == 0:
            return None, None
        
        face_crop = extract_face_from_retinaface(img_rgb, faces)
        if face_crop is None:
            return None, None
        
        face_bgr = cv2.cvtColor(face_crop, cv2.COLOR_RGB2BGR)
        insight_faces = app.get(face_bgr)
        
        if not insight_faces:
            return None, None
        
        face = insight_faces[0]
        embedding = face.embedding.astype('float32')
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding, face_crop
        
    except Exception as e:
        print(f"Error processing frame: {e}")
        return None, None
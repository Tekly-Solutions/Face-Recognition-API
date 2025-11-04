"""Verification logic"""
import os
import numpy as np
from src.core.image_processor import process_single_image

def verify_embedding(index, labels, embedding, threshold):
    """Verify an embedding against the database"""
    if index is None or embedding is None:
        return None, 0.0
    
    D, I = index.search(np.array([embedding]).astype('float32'), k=1)
    
    top_score = float(D[0][0])
    top_label = labels[I[0][0]]
    
    if top_score >= threshold:
        return top_label, top_score
    else:
        return None, top_score

def verify_face(app, index, labels, image_path, threshold):
    """Verify a face against the database"""
    if index is None:
        print("❌ No index built yet")
        return None, 0.0
    
    print(f"🔍 Verifying: {os.path.basename(image_path)}")
    
    embedding = process_single_image(app, image_path, "query")
    
    if embedding is None:
        print("❌ Could not process query image")
        return None, 0.0
    
    label, score = verify_embedding(index, labels, embedding, threshold)
    
    if label:
        print(f"✅ Match: {label} (score: {score:.3f})")
    else:
        print(f"❌ No match (score: {score:.3f}, threshold: {threshold:.3f})")
    
    return label, score
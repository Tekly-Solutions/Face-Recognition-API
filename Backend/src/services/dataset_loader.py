"""Dataset loading"""
import os
import numpy as np
from src.core.image_processor import process_single_image

def load_dataset(app, dataset_path):
    """Load dataset using the proven method"""
    print(f"📂 Loading dataset from: {dataset_path}")
    
    embeddings = []
    labels = []
    total_images = 0
    successful_images = 0
    
    for person_folder in os.listdir(dataset_path):
        person_path = os.path.join(dataset_path, person_folder)
        
        if not os.path.isdir(person_path):
            continue
        
        print(f"\n👤 Processing: {person_folder}")
        
        for image_file in os.listdir(person_path):
            if not image_file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                continue
            
            image_path = os.path.join(person_path, image_file)
            total_images += 1
            
            embedding = process_single_image(app, image_path, person_folder)
            
            if embedding is not None:
                embeddings.append(embedding)
                labels.append(person_folder)
                successful_images += 1
    
    embeddings = np.array(embeddings) if embeddings else np.array([])
    labels = np.array(labels) if labels else np.array([])
    
    print(f"\n{'='*60}")
    print(f"📊 DATASET LOADING SUMMARY:")
    print(f"Total images processed: {total_images}")
    print(f"Successful embeddings: {successful_images}")
    print(f"Failed images: {total_images - successful_images}")
    print(f"Success rate: {successful_images/total_images*100:.1f}%" if total_images > 0 else "0%")
    print(f"Classes: {list(set(labels))}")
    print(f"{'='*60}")
    
    return embeddings, labels, len(embeddings) > 0
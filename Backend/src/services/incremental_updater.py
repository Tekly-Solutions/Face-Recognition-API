"""Incremental model update service - Add new faces, remove missing ones"""
import os
import numpy as np
from src.core.image_processor import process_single_image
from src.services.index_manager import build_index
from src.services.storage_service import save_model


def get_existing_persons(labels):
    """Get set of unique persons currently in model"""
    if len(labels) == 0:
        return set()
    return set(labels)


def get_firebase_persons(dataset_path):
    """Get set of persons in Firebase (dataset folder)"""
    firebase_persons = set()
    
    if not os.path.exists(dataset_path):
        return firebase_persons
    
    for folder in os.listdir(dataset_path):
        person_path = os.path.join(dataset_path, folder)
        if os.path.isdir(person_path):
            # Check if folder has any images
            images = [f for f in os.listdir(person_path) 
                     if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
            if len(images) > 0:
                firebase_persons.add(folder)
    
    return firebase_persons


def get_person_embeddings(app, dataset_path, person_name):
    """Get embeddings for a specific person"""
    embeddings = []
    person_path = os.path.join(dataset_path, person_name)
    
    if not os.path.isdir(person_path):
        return np.array([])
    
    for image_file in os.listdir(person_path):
        if not image_file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            continue
        
        image_path = os.path.join(person_path, image_file)
        embedding = process_single_image(app, image_path, person_name)
        
        if embedding is not None:
            embeddings.append(embedding)
    
    return np.array(embeddings) if embeddings else np.array([])


def incremental_update(app, dataset_path, current_embeddings, current_labels, 
                       current_index, threshold):
    """
    Incrementally update model:
    - Add new persons/embeddings from Firebase
    - Remove persons no longer in Firebase
    - Keep existing embeddings for unchanged persons
    
    Returns: (new_embeddings, new_labels, new_index, changes_made)
    """
    print("\n" + "="*70)
    print("🔄 INCREMENTAL MODEL UPDATE")
    print("="*70)
    
    # Get current state
    existing_persons = get_existing_persons(current_labels)
    firebase_persons = get_firebase_persons(dataset_path)
    
    print(f"\n📊 Current Model State:")
    print(f"   Persons in model: {len(existing_persons)}")
    print(f"   Total embeddings: {len(current_labels)}")
    print(f"   Persons list: {sorted(existing_persons)}")
    
    print(f"\n📂 Firebase State:")
    print(f"   Persons in Firebase: {len(firebase_persons)}")
    print(f"   Persons list: {sorted(firebase_persons)}")
    
    # Find differences
    persons_to_remove = existing_persons - firebase_persons
    persons_to_add = firebase_persons - existing_persons
    persons_unchanged = existing_persons & firebase_persons
    
    print(f"\n🔍 Changes Detected:")
    print(f"   To add: {len(persons_to_add)} person(s) - {sorted(persons_to_add)}")
    print(f"   To remove: {len(persons_to_remove)} person(s) - {sorted(persons_to_remove)}")
    print(f"   Unchanged: {len(persons_unchanged)} person(s)")
    
    if len(persons_to_add) == 0 and len(persons_to_remove) == 0:
        print("\n✅ No changes needed. Model is up to date.")
        return current_embeddings, current_labels, current_index, False
    
    # Build new model
    new_embeddings = []
    new_labels = []
    
    # 1. Keep embeddings for unchanged persons
    print(f"\n📌 Keeping embeddings for unchanged persons...")
    for i, label in enumerate(current_labels):
        if label in persons_unchanged:
            new_embeddings.append(current_embeddings[i])
            new_labels.append(label)
    
    unchanged_count = len(new_embeddings)
    print(f"   ✅ Kept {unchanged_count} embeddings from unchanged persons")
    
    # 2. Add new persons
    if len(persons_to_add) > 0:
        print(f"\n➕ Adding new persons from Firebase...")
        for person_name in sorted(persons_to_add):
            print(f"   👤 Processing: {person_name}")
            person_embeddings = get_person_embeddings(app, dataset_path, person_name)
            
            if len(person_embeddings) > 0:
                for embedding in person_embeddings:
                    new_embeddings.append(embedding)
                    new_labels.append(person_name)
                print(f"      ✅ Added {len(person_embeddings)} embeddings")
            else:
                print(f"      ⚠️ No valid embeddings for {person_name}")
    
    # Convert to numpy arrays
    new_embeddings = np.array(new_embeddings) if new_embeddings else np.array([])
    new_labels = np.array(new_labels) if new_labels else np.array([])
    
    # 3. Build new index
    new_index = None
    if len(new_embeddings) > 0:
        print(f"\n🔍 Building new FAISS index...")
        new_index = build_index(new_embeddings)
    else:
        print(f"\n⚠️ No embeddings in updated model!")
    
    # 4. Save updated model
    if new_index is not None:
        print(f"\n💾 Saving updated model...")
        save_model(new_embeddings, new_labels, threshold, new_index)
    
    # Summary
    print(f"\n" + "="*70)
    print(f"✅ UPDATE COMPLETE")
    print(f"{'='*70}")
    print(f"Previous state: {len(current_labels)} embeddings, {len(existing_persons)} persons")
    print(f"New state:      {len(new_labels)} embeddings, {len(set(new_labels)) if len(new_labels) > 0 else 0} persons")
    print(f"Changes:")
    print(f"  + Added:   {len(persons_to_add)} new person(s)")
    print(f"  - Removed: {len(persons_to_remove)} person(s)")
    print(f"  → Kept:    {unchanged_count} embeddings from unchanged persons")
    print(f"{'='*70}\n")
    
    return new_embeddings, new_labels, new_index, True


def full_rebuild_needed(embeddings, labels, index):
    """Check if full rebuild is needed (fallback)"""
    return (len(embeddings) == 0 or 
            len(labels) == 0 or 
            index is None or
            len(embeddings) != len(labels))

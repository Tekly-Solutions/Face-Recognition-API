"""Model evaluation script"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.storage_service import load_model

def evaluate():
    """Evaluate model performance"""
    print("Evaluating model...")
    
    embeddings, labels, threshold, index, success = load_model()
    
    if success:
        print(f"\nModel Statistics:")
        print(f"Total embeddings: {len(embeddings)}")
        print(f"Unique classes: {len(set(labels))}")
        print(f"Classes: {list(set(labels))}")
        print(f"Threshold: {threshold}")
    else:
        print("Failed to load model")

if __name__ == "__main__":
    evaluate()
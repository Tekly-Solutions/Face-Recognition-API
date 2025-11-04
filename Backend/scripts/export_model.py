"""Model export utility"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.storage_service import load_model, save_model

def export_model(output_path):
    """Export model to specified path"""
    print(f"Exporting model to: {output_path}")
    
    embeddings, labels, threshold, index, success = load_model()
    
    if success:
        save_model(embeddings, labels, threshold, index, output_path)
        print("Export complete!")
    else:
        print("Failed to load model")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        export_model(sys.argv[1])
    else:
        print("Usage: python export_model.py <output_path>")
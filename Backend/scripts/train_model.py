"""Model training script"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


from config.config import dataset_config
from src.core.embedding_service import init_insightface
from src.services.dataset_loader import load_dataset
from src.services.index_manager import build_index
from src.services.storage_service import save_model

def train():
    """Train and save model"""
    print("Starting model training...")
    
    app = init_insightface()
    embeddings, labels, success = load_dataset(app, dataset_config.dataset_path)
    
    if success:
        index = build_index(embeddings)
        if index:
            save_model(embeddings, labels, 0.6, index)
            print("Model training complete!")
        else:
            print("Failed to build index")
    else:
        print("Failed to load dataset")

if __name__ == "__main__":
    train()
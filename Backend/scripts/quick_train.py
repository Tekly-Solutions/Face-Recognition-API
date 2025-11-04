"""Standalone script for quick face training"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.config import dataset_config
from src.core.embedding_service import init_insightface
from src.services.camera_service import close_camera
from src.services.training_service import quick_train_face
from src.services.dataset_loader import load_dataset
from src.services.index_manager import build_index
from src.services.storage_service import save_model

def main():
    """Quick training script"""
    print("="*60)
    print("🎓 QUICK FACE TRAINING TOOL")
    print("="*60)
    
    # Initialize
    app = init_insightface()
    camera = None
    dataset_path = dataset_config.dataset_path
    
    # Ensure dataset directory exists
    os.makedirs(dataset_path, exist_ok=True)
    
    try:
        # Train new face
        success, camera, person_name = quick_train_face(app, camera, dataset_path)
        
        if success:
            print("\n" + "="*60)
            print("Rebuild model with new face?")
            rebuild = input("(y/n): ").lower().strip()
            
            if rebuild == 'y':
                print("\n🔨 Rebuilding model...")
                embeddings, labels, load_success = load_dataset(app, dataset_path)
                
                if load_success and len(embeddings) > 0:
                    index = build_index(embeddings)
                    if index:
                        save_model(embeddings, labels, 0.6, index)
                        print("\n🎉 Model rebuilt successfully!")
                        print(f"✅ '{person_name}' is now in the system!")
                    else:
                        print("\n❌ Failed to build index")
                else:
                    print("\n❌ Failed to load dataset")
            else:
                print("\n💡 Training images saved.")
                print("Run 'python scripts/train_model.py' to rebuild the model.")
        else:
            print("\n❌ Training failed or cancelled")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Training interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        close_camera(camera)
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()
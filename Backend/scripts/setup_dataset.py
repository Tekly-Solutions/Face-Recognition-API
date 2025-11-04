"""Dataset setup utility"""
import os
import sys

def setup_dataset():
    """Create dataset directory structure"""
    print("Setting up dataset structure...")
    
    dataset_dir = "dataset"
    os.makedirs(dataset_dir, exist_ok=True)
    
    print(f"Dataset directory created: {dataset_dir}")
    print("\nInstructions:")
    print("1. Create a folder for each person inside 'dataset/'")
    print("2. Add 3-5 images per person")
    print("3. Use clear, frontal face images")
    print("\nExample structure:")
    print("dataset/")
    print("  person1/")
    print("    image1.jpg")
    print("    image2.jpg")
    print("  person2/")
    print("    image1.jpg")

if __name__ == "__main__":
    setup_dataset()
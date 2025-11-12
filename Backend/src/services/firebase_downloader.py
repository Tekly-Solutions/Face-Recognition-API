import os
from firebase_admin import storage
from config.firebase_config import *

def download_all_faces(dataset_folder: str = "dataset"):
    """
    Downloads all folders and images under 'faces/' from Firebase Storage
    and saves them in the dataset folder with the same structure.
    Skips images that already exist locally.
    """
    try:
        bucket = storage.bucket()
        
        # Test connection first
        print("🔌 Testing Firebase Storage connection...")
        blobs = list(bucket.list_blobs(prefix="faces/", max_results=1))
        print("✅ Firebase Storage connection successful!")
        
    except Exception as e:
        if "Invalid JWT Signature" in str(e) or "invalid_grant" in str(e):
            print(f"❌ Firebase authentication failed: Invalid credentials")
            print(f"💡 The ServiceAccountKey.json file may be:")
            print(f"   - Corrupted or incomplete")
            print(f"   - Expired (download a new one from Firebase Console)")
            print(f"   - Not from the correct Firebase project")
            print(f"\n📋 To fix:")
            print(f"   1. Go to https://console.firebase.google.com")
            print(f"   2. Select project: talentnest-tekly")
            print(f"   3. Settings → Service Accounts")
            print(f"   4. Generate New Private Key")
            print(f"   5. Replace Backend/ServiceAccountKey.json")
        else:
            print(f"❌ Firebase Storage error: {e}")
        raise
    
    bucket = storage.bucket()
    blobs = bucket.list_blobs(prefix="faces/")

    total_downloaded = 0
    for blob in blobs:
        if blob.name.endswith("/"):  # skip folders
            continue

        # Example: faces/user1/img1.jpg → dataset/user1/img1.jpg
        parts = blob.name.split("/")
        if len(parts) < 3:
            continue  # not in expected format

        user_id = parts[1]
        file_name = parts[-1]

        user_folder = os.path.join(dataset_folder, user_id)
        os.makedirs(user_folder, exist_ok=True)

        local_path = os.path.join(user_folder, file_name)

        # Skip download if file already exists
        if os.path.exists(local_path):
            # print(f"⚠️ Skipping already downloaded: {local_path}")
            continue

        blob.download_to_filename(local_path)
        total_downloaded += 1
        print(f"✅ Downloaded: {blob.name} → {local_path}")

    print(f"\n🎉 All done! Total new images downloaded: {total_downloaded}")
    return total_downloaded

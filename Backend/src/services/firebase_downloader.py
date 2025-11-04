import os
from firebase_admin import storage
from config.firebase_config import *

def download_all_faces(dataset_folder: str = "dataset"):
    """
    Downloads all folders and images under 'faces/' from Firebase Storage
    and saves them in the dataset folder with the same structure.
    Skips images that already exist locally.
    """
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

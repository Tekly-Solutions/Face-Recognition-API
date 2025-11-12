import os
import firebase_admin
from firebase_admin import credentials, storage

# Construct path relative to this config file
config_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(config_dir)
key_path = os.path.join(backend_dir, 'ServiceAccountKey.json')

# Initialize Firebase with proper error handling
# Check if already initialized to prevent double initialization
if not firebase_admin._apps:
    try:
        if not os.path.exists(key_path):
            raise FileNotFoundError(f"ServiceAccountKey.json not found at: {key_path}")
        
        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'talentnest-tekly.firebasestorage.app'
        })
        print(f"✅ Firebase connected successfully!")
        print(f"📍 Using credentials: {key_path}")
        
    except FileNotFoundError as e:
        print(f"❌ {e}")
        raise
    except ValueError as e:
        if "already exists" in str(e):
            print(f"⚠️ Firebase app already initialized")
        else:
            print(f"❌ Firebase initialization error: {e}")
            raise
    except Exception as e:
        print(f"❌ Firebase initialization error: {e}")
        raise
else:
    print(f"⚠️ Firebase already initialized, using existing instance")
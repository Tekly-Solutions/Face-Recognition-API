#!/usr/bin/env python3
"""
Quick test to verify Firebase connection is working
"""
import os
import sys

print("=" * 60)
print("🔧 Testing Firebase Connection")
print("=" * 60)

# Check if ServiceAccountKey.json exists
key_path = os.path.join(os.path.dirname(__file__), 'ServiceAccountKey.json')
print(f"\n📂 Checking for credentials file...")
print(f"   Expected path: {key_path}")
print(f"   File exists: {os.path.exists(key_path)}")

if not os.path.exists(key_path):
    print(f"\n❌ ERROR: ServiceAccountKey.json not found!")
    sys.exit(1)

print(f"✅ File found!")

# Try to import Firebase config
print(f"\n🔌 Attempting Firebase initialization...")
try:
    # Add Backend to path
    sys.path.insert(0, os.path.dirname(__file__))
    
    from config.firebase_config import storage
    print(f"✅ Firebase initialized successfully!")
    
    # Try to get bucket
    print(f"\n📦 Testing bucket access...")
    bucket = storage.bucket()
    print(f"✅ Bucket accessible: {bucket.name}")
    
    print(f"\n" + "=" * 60)
    print(f"✅ ALL TESTS PASSED - Firebase is working!")
    print(f"=" * 60)
    
except Exception as e:
    print(f"\n❌ ERROR during Firebase initialization:")
    print(f"   {type(e).__name__}: {e}")
    sys.exit(1)

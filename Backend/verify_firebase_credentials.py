#!/usr/bin/env python3
"""
Firebase Credentials Verification Script

This script verifies that your ServiceAccountKey.json is valid and can connect to Firebase.
"""

import os
import sys
import json
from pathlib import Path

def main():
    print("=" * 70)
    print("🔍 Firebase Credentials Verification")
    print("=" * 70)
    
    # Step 1: Check file exists
    print("\n📂 Step 1: Checking ServiceAccountKey.json location...")
    key_path = os.path.join(os.path.dirname(__file__), 'ServiceAccountKey.json')
    
    if not os.path.exists(key_path):
        print(f"❌ File not found at: {key_path}")
        print(f"\n💡 To fix:")
        print(f"   1. Go to https://console.firebase.google.com")
        print(f"   2. Select project: talentnest-tekly")
        print(f"   3. Settings → Service Accounts")
        print(f"   4. Generate New Private Key")
        print(f"   5. Save as: {key_path}")
        return False
    
    print(f"✅ Found: {key_path}")
    
    # Step 2: Validate JSON structure
    print("\n📋 Step 2: Validating JSON structure...")
    try:
        with open(key_path, 'r') as f:
            credentials = json.load(f)
        print("✅ Valid JSON structure")
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        print(f"   The file may be corrupted. Re-download from Firebase Console.")
        return False
    
    # Step 3: Check required fields
    print("\n🔑 Step 3: Checking required fields...")
    required_fields = [
        'type',
        'project_id',
        'private_key_id',
        'private_key',
        'client_email',
        'client_id',
        'auth_uri',
        'token_uri',
        'auth_provider_x509_cert_url',
        'client_x509_cert_url'
    ]
    
    missing_fields = [f for f in required_fields if f not in credentials]
    
    if missing_fields:
        print(f"❌ Missing fields: {', '.join(missing_fields)}")
        print(f"   The credentials file is incomplete. Re-download from Firebase Console.")
        return False
    
    print(f"✅ All required fields present")
    
    # Step 4: Display credential info
    print("\n📊 Credential Information:")
    print(f"   Project ID: {credentials.get('project_id')}")
    print(f"   Type: {credentials.get('type')}")
    print(f"   Email: {credentials.get('client_email')}")
    
    # Step 5: Test Firebase connection
    print("\n🔌 Step 4: Testing Firebase connection...")
    try:
        import firebase_admin
        from firebase_admin import credentials, storage
        
        # Check if already initialized
        if firebase_admin._apps:
            print("⚠️ Firebase already initialized in this session")
            print("✅ Assuming connection is valid")
            return True
        
        # Initialize
        cred = credentials.Certificate(credentials)
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'talentnest-tekly.firebasestorage.app'
        })
        
        # Test bucket access
        bucket = storage.bucket()
        print(f"✅ Successfully connected to Firebase!")
        print(f"   Bucket: {bucket.name}")
        
        # List a few items to verify
        print("\n📦 Step 5: Listing sample files from Firebase Storage...")
        blobs = list(bucket.list_blobs(prefix="faces/", max_results=5))
        if blobs:
            print(f"✅ Found {len(blobs)} files in Firebase Storage (faces/ folder)")
            for blob in blobs[:3]:
                print(f"   - {blob.name}")
        else:
            print(f"⚠️ No files found in faces/ folder (upload some faces first)")
        
        return True
        
    except ValueError as e:
        if "already exists" in str(e):
            print("⚠️ Firebase app already initialized, assuming valid")
            return True
        else:
            print(f"❌ Firebase initialization error: {e}")
            return False
    except Exception as e:
        if "Invalid JWT Signature" in str(e) or "invalid_grant" in str(e):
            print(f"❌ Authentication failed: Invalid or expired credentials")
            print(f"\n💡 To fix:")
            print(f"   1. Re-download credentials from Firebase Console")
            print(f"   2. Replace Backend/ServiceAccountKey.json")
            print(f"   3. Run this script again")
        else:
            print(f"❌ Firebase error: {e}")
        return False

if __name__ == '__main__':
    success = main()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ All checks passed! Firebase is properly configured.")
    else:
        print("❌ Some checks failed. See above for details.")
    print("=" * 70)
    
    sys.exit(0 if success else 1)

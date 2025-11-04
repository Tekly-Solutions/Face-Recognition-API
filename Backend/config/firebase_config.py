import firebase_admin
from firebase_admin import credentials, storage

# Replace with your Firebase service account JSON path
cred = credentials.Certificate(
    "D:\TEKLY Solutions\TalentNest Project\Face-Recognition-API/serviceAccountKey.json"
)

# Replace with your Firebase Storage bucket name
firebase_admin.initialize_app(cred, {
    'storageBucket': 'talentnest-tekly.firebasestorage.app'
})

print("Firebase connected successfully!")
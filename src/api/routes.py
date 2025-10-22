
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import os

router = APIRouter()

@router.post("/train")
async def train_face(file: UploadFile = File(...), label: str = Form(...)):
    # Save uploaded image into dataset/<label>/
    dataset_dir = os.path.join("dataset", label)
    os.makedirs(dataset_dir, exist_ok=True)
    # Use a unique filename to avoid overwriting
    filename = file.filename
    save_path = os.path.join(dataset_dir, filename)
    with open(save_path, "wb") as f:
        f.write(await file.read())
    return {"success": True, "message": f"Image saved to {save_path}"}

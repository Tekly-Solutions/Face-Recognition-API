"""Input validation utilities"""
import os
from typing import Optional

def validate_image_path(image_path: str) -> bool:
    """Validate image file path"""
    if not os.path.exists(image_path):
        return False
    
    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
    return image_path.lower().endswith(valid_extensions)

def validate_threshold(threshold: float) -> bool:
    """Validate threshold value"""
    return 0.0 <= threshold <= 1.0

def validate_camera_id(camera_id: int) -> bool:
    """Validate camera ID"""
    return camera_id >= 0
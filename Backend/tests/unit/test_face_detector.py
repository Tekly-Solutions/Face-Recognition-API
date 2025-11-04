"""Unit tests for face detector"""
import pytest
import numpy as np
from src.core.face_detector import extract_face_from_retinaface

def test_extract_face_valid():
    """Test face extraction with valid input"""
    img_rgb = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    faces = {
        'face_1': {
            'facial_area': [100, 100, 200, 200]
        }
    }
    
    result = extract_face_from_retinaface(img_rgb, faces)
    assert result is not None
    assert result.shape == (100, 100, 3)
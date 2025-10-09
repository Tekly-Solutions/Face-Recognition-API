"""
Configuration Module optimized for NVIDIA GeForce MX330 (2GB VRAM)

Copyright (c) 2025 Tekly IT Solutions. All rights reserved.
PROPRIETARY SOFTWARE - Commercial use requires a valid license agreement.
"""
from dataclasses import dataclass
from typing import Tuple

@dataclass
class GPUConfig:
    """GPU settings optimized for MX330"""
    use_gpu: bool = True
    gpu_id: int = 0
    batch_size: int = 8  # Smaller batch for 2GB VRAM
    fallback_to_cpu: bool = True

@dataclass
class ModelConfig:
    """Model settings optimized for 2GB VRAM"""
    detection_size: Tuple[int, int] = (320, 320)  # Smaller to fit in VRAM
    threshold: float = 0.6
    embedding_dim: int = 512

@dataclass
class CameraConfig:
    """Camera settings for MX330"""
    frame_width: int = 640  # Moderate resolution
    frame_height: int = 480
    fps: int = 30  # Realistic for MX330

@dataclass
class DatasetConfig:
    dataset_path: str = "dataset"
    supported_formats: tuple = ('.jpg', '.jpeg', '.png', '.bmp')

@dataclass
class StorageConfig:
    model_path: str = "models/enhanced_face_model.pkl"
    index_path: str = "models/enhanced_face_index.faiss"
    use_gpu_index: bool = False  # Keep FAISS on CPU for MX330

gpu_config = GPUConfig()
model_config = ModelConfig()
camera_config = CameraConfig()
dataset_config = DatasetConfig()
storage_config = StorageConfig()

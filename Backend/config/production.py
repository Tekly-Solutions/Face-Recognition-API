"""Production environment config"""
from config.config import ModelConfig, CameraConfig

model_config = ModelConfig(
    detection_size=(320, 320),  # Higher quality
    threshold=0.7  # Stricter threshold
)

camera_config = CameraConfig(
    frame_width=1280,
    frame_height=720,
    fps=30
)
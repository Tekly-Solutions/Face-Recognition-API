"""Development environment config"""
from config.config import ModelConfig, CameraConfig

model_config = ModelConfig(
    detection_size=(160, 160),
    threshold=0.5  # Lower threshold for testing
)

camera_config = CameraConfig(
    frame_width=640,
    frame_height=480,
    fps=30
)
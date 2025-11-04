"""Helper utilities"""
import os
from datetime import datetime

def ensure_directory_exists(directory: str):
    """Create directory if it doesn't exist"""
    os.makedirs(directory, exist_ok=True)

def generate_timestamp():
    """Generate timestamp string"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def format_confidence_score(score: float) -> str:
    """Format confidence score for display"""
    return f"{score:.3f}"
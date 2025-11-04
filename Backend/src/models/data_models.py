"""Data models"""
from dataclasses import dataclass
from typing import Optional
import numpy as np

@dataclass
class FaceEmbedding:
    """Face embedding data structure"""
    embedding: np.ndarray
    label: str
    confidence: float = 0.0
    
@dataclass
class VerificationResult:
    """Verification result structure"""
    identity: Optional[str]
    confidence: float
    success: bool
    timestamp: str
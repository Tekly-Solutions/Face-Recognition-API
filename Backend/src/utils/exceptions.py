"""Custom exceptions"""

class FaceVerificationError(Exception):
    """Base exception"""
    pass

class FaceDetectionError(FaceVerificationError):
    """Face detection failed"""
    pass

class EmbeddingError(FaceVerificationError):
    """Embedding extraction failed"""
    pass

class CameraError(FaceVerificationError):
    """Camera operation failed"""
    pass
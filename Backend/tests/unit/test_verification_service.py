"""Unit tests for verification service"""
import pytest
import numpy as np
import faiss

def test_build_index():
    """Test FAISS index building"""
    from src.services.index_manager import build_index
    
    embeddings = np.random.rand(10, 512).astype('float32')
    index = build_index(embeddings)
    
    assert index is not None
    assert index.ntotal == 10
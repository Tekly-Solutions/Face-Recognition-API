"""Pytest configuration"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

@pytest.fixture
def sample_image_path():
    """Sample image path for testing"""
    return "tests/fixtures/images/test_face.jpg"

@pytest.fixture
def temp_dataset_path(tmp_path):
    """Temporary dataset path"""
    return str(tmp_path / "test_dataset")
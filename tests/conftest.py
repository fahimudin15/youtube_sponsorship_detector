import pytest
import os
import json
from datetime import datetime

@pytest.fixture
def sample_video_data():
    return {
        'video_id': 'test_video_123',
        'title': 'Test Video',
        'description': 'This is a test video with some product placement',
        'published_at': datetime.utcnow().isoformat()
    }

@pytest.fixture
def sample_segments():
    return [
        {
            'text': 'Welcome to the video',
            'start_time': 0,
            'end_time': 10,
            'is_sponsored': False,
            'confidence': 0.1
        },
        {
            'text': 'Check out this amazing product',
            'start_time': 10,
            'end_time': 20,
            'is_sponsored': True,
            'confidence': 0.95
        },
        {
            'text': 'Back to regular content',
            'start_time': 20,
            'end_time': 30,
            'is_sponsored': False,
            'confidence': 0.2
        }
    ]

@pytest.fixture
def temp_data_dir(tmp_path):
    """Create a temporary data directory structure"""
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()
    processed_dir.mkdir()
    return tmp_path

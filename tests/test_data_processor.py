import pytest
from src.data_processor import DataProcessor
import os

@pytest.fixture
def data_processor():
    return DataProcessor()

@pytest.fixture
def sample_transcript():
    return [
        {'text': 'First segment', 'start': 0.0, 'duration': 5.0},
        {'text': 'Second segment', 'start': 5.0, 'duration': 5.0},
        {'text': 'Third segment', 'start': 10.0, 'duration': 5.0},
        {'text': 'Fourth segment', 'start': 15.0, 'duration': 5.0},
        {'text': 'Fifth segment', 'start': 20.0, 'duration': 5.0}
    ]

def test_preprocess_text(data_processor):
    # Test basic preprocessing
    text = "Check out THIS Product at http://example.com! #ad"
    processed = data_processor.preprocess_text(text)
    assert processed == "check out this product at ad"
    
    # Test empty text
    assert data_processor.preprocess_text("") == ""
    
    # Test text with special characters
    text = "Product! @#$%^& 123 Review"
    assert data_processor.preprocess_text(text) == "product 123 review"

def test_create_transcript_windows(data_processor, sample_transcript):
    # Test with default window size and stride
    windows = data_processor.create_transcript_windows(sample_transcript)
    assert len(windows) > 0
    assert 'text' in windows[0]
    assert 'start_time' in windows[0]
    assert 'end_time' in windows[0]
    
    # Test with custom window size
    windows = data_processor.create_transcript_windows(sample_transcript, window_size=2, stride=1)
    assert len(windows) == 4  # Should have 4 windows with size 2 and stride 1
    
    # Test with empty transcript
    assert data_processor.create_transcript_windows([]) == []

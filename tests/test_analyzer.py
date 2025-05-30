import pytest
from datetime import datetime
from src.analyzer import VideoAnalyzer

def test_init_video_analyzer():
    analyzer = VideoAnalyzer()
    assert analyzer.data_processor is not None
    assert analyzer.model_trainer is not None

def test_group_sponsored_segments():
    analyzer = VideoAnalyzer()
    
    # Test with empty segments
    assert analyzer._group_sponsored_segments([]) == []
    
    # Test with no sponsored segments
    test_segments = [
        {'start_time': 0, 'end_time': 10, 'is_sponsored': False, 'confidence': 0.1},
        {'start_time': 10, 'end_time': 20, 'is_sponsored': False, 'confidence': 0.2}
    ]
    assert analyzer._group_sponsored_segments(test_segments) == []
    
    # Test with consecutive sponsored segments
    test_segments = [
        {'start_time': 0, 'end_time': 10, 'is_sponsored': True, 'confidence': 0.8},
        {'start_time': 10, 'end_time': 20, 'is_sponsored': True, 'confidence': 0.9}
    ]
    result = analyzer._group_sponsored_segments(test_segments)
    assert len(result) == 1
    assert result[0]['start_time'] == 0
    assert result[0]['end_time'] == 20
    assert result[0]['confidence'] == pytest.approx(0.85)  # Average of 0.8 and 0.9
    
    # Test with non-consecutive sponsored segments
    test_segments = [
        {'start_time': 0, 'end_time': 10, 'is_sponsored': True, 'confidence': 0.8},
        {'start_time': 10, 'end_time': 20, 'is_sponsored': False, 'confidence': 0.2},
        {'start_time': 20, 'end_time': 30, 'is_sponsored': True, 'confidence': 0.9}
    ]
    result = analyzer._group_sponsored_segments(test_segments)
    assert len(result) == 2
    assert result[0]['start_time'] == 0
    assert result[0]['end_time'] == 10
    assert result[1]['start_time'] == 20
    assert result[1]['end_time'] == 30

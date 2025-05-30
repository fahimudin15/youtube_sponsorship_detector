from typing import Dict, List, Optional
from .data_processor import DataProcessor
from .model import ModelTrainer
import json
import os
from datetime import datetime

class VideoAnalyzer:
    def __init__(self, model_path: str = None):
        self.data_processor = DataProcessor()
        self.model_trainer = ModelTrainer()
        if model_path:
            self.model_trainer.load_model(model_path)
        
    def analyze_video(self, video_id: str, threshold: float = 0.5) -> Dict:
        """
        Analyze a video for sponsorship segments
        Args:
            video_id: YouTube video ID
            threshold: Confidence threshold for sponsorship detection
        Returns:
            Dictionary containing analysis results
        """
        # Process video segments
        segments = self.data_processor.process_video_segments(video_id)
        if not segments:
            return {
                'video_id': video_id,
                'status': 'error',
                'message': 'No segments found for analysis'
            }
        
        # Get predictions for each segment
        predictions = self.model_trainer.predict_segments(segments, threshold)
        
        # Group consecutive sponsored segments
        sponsored_regions = self._group_sponsored_segments(predictions)
        
        return {
            'video_id': video_id,
            'status': 'success',
            'analyzed_at': datetime.utcnow().isoformat(),
            'threshold': threshold,
            'sponsored_regions': sponsored_regions,
            'segments': predictions
        }
    
    def _group_sponsored_segments(self, segments: List[Dict]) -> List[Dict]:
        """
        Group consecutive sponsored segments into regions
        """
        regions = []
        current_region = None
        
        for segment in segments:
            if segment['is_sponsored']:
                if current_region is None:
                    current_region = {
                        'start_time': segment['start_time'],
                        'end_time': segment['end_time'],
                        'confidence': [segment['confidence']]
                    }
                else:
                    current_region['end_time'] = segment['end_time']
                    current_region['confidence'].append(segment['confidence'])
            else:
                if current_region is not None:
                    current_region['confidence'] = sum(current_region['confidence']) / len(current_region['confidence'])
                    regions.append(current_region)
                    current_region = None
        
        # Add final region if exists
        if current_region is not None:
            current_region['confidence'] = sum(current_region['confidence']) / len(current_region['confidence'])
            regions.append(current_region)
        
        return regions
    
    def save_results(self, results: Dict, output_dir: str = "data/processed") -> str:
        """
        Save analysis results to a JSON file
        """
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{results['video_id']}_analysis.json")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        return output_file

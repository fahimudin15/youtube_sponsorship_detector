import os
import json
import pandas as pd
from typing import List, Dict, Tuple
import re
from sklearn.model_selection import train_test_split
from transformers import AutoTokenizer

class DataProcessor:
    def __init__(self, raw_data_dir: str = "data/raw", processed_data_dir: str = "data/processed"):
        self.raw_data_dir = raw_data_dir
        self.processed_data_dir = processed_data_dir
        self.tokenizer = AutoTokenizer.from_pretrained('distilbert-base-uncased')
        
    def load_raw_data(self) -> List[Dict]:
        """Load all raw video data from the data directory"""
        data = []
        for filename in os.listdir(self.raw_data_dir):
            if filename.endswith('_details.json'):
                video_id = filename.replace('_details.json', '')
                video_data = self._load_video_data(video_id)
                if video_data:
                    data.append(video_data)
        return data

    def _load_video_data(self, video_id: str) -> Dict:
        """Load details and transcript for a single video"""
        details_file = os.path.join(self.raw_data_dir, f"{video_id}_details.json")
        transcript_file = os.path.join(self.raw_data_dir, f"{video_id}_transcript.json")
        
        try:
            with open(details_file, 'r', encoding='utf-8') as f:
                details = json.load(f)
            
            transcript = []
            if os.path.exists(transcript_file):
                with open(transcript_file, 'r', encoding='utf-8') as f:
                    transcript = json.load(f)
            
            return {
                'video_id': video_id,
                'title': details['title'],
                'description': details['description'],
                'transcript': ' '.join([item['text'] for item in transcript])
            }
        except Exception as e:
            print(f"Error loading data for video {video_id}: {str(e)}")
            return None

    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text data"""
        # Convert to lowercase
        text = text.lower()
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        # Remove special characters and numbers
        text = re.sub(r'[^\w\s]', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text

    def prepare_training_data(self, labeled_data: List[Dict]) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Prepare data for model training
        labeled_data should be a list of dicts with 'text' and 'is_sponsored' fields
        """
        # Create DataFrame
        df = pd.DataFrame(labeled_data)
        
        # Preprocess text
        df['processed_text'] = df['text'].apply(self.preprocess_text)
        
        # Split into training and validation sets
        train_df, val_df = train_test_split(df, test_size=0.2, random_state=42)
        
        return train_df, val_df

    def tokenize_text(self, texts: List[str], max_length: int = 512) -> Dict:
        """Tokenize text data for the model"""
        return self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=max_length,
            return_tensors='pt'
        )

    def create_transcript_windows(self, transcript: List[Dict], window_size: int = 5, stride: int = 2) -> List[Dict]:
        """
        Create sliding windows over transcript segments for timestamp detection
        Args:
            transcript: List of transcript segments with 'text' and 'start' time
            window_size: Number of segments to include in each window
            stride: Number of segments to move forward for next window
        Returns:
            List of windows with combined text and start/end times
        """
        windows = []
        for i in range(0, len(transcript), stride):
            window_end = min(i + window_size, len(transcript))
            window_segments = transcript[i:window_end]
            if len(window_segments) < window_size:  # Skip incomplete windows
                break
                
            window = {
                'text': ' '.join([seg['text'] for seg in window_segments]),
                'start_time': window_segments[0]['start'],
                'end_time': window_segments[-1]['start'] + window_segments[-1]['duration']
            }
            windows.append(window)
        return windows

    def process_video_segments(self, video_id: str) -> List[Dict]:
        """
        Process video transcript into segments for sponsorship detection
        """
        transcript_file = os.path.join(self.raw_data_dir, f"{video_id}_transcript.json")
        if not os.path.exists(transcript_file):
            return []
            
        with open(transcript_file, 'r', encoding='utf-8') as f:
            transcript = json.load(f)
            
        # Create sliding windows over transcript
        windows = self.create_transcript_windows(transcript)
        
        # Preprocess text in each window
        for window in windows:
            window['processed_text'] = self.preprocess_text(window['text'])
            
        return windows

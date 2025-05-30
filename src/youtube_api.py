from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
import os
from typing import Dict, List, Optional
from datetime import datetime
import json

class YouTubeAPI:
    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)

    def get_video_details(self, video_id: str) -> Optional[Dict]:
        """
        Fetch video details including title, description, and other metadata
        """
        try:
            request = self.youtube.videos().list(
                part="snippet,contentDetails",
                id=video_id
            )
            response = request.execute()
            
            if not response['items']:
                return None
                
            video_data = response['items'][0]
            return {
                'video_id': video_id,
                'title': video_data['snippet']['title'],
                'description': video_data['snippet']['description'],
                'published_at': video_data['snippet']['publishedAt'],
                'channel_id': video_data['snippet']['channelId'],
                'channel_title': video_data['snippet']['channelTitle'],
                'duration': video_data['contentDetails']['duration']
            }
        except Exception as e:
            print(f"Error fetching video details for {video_id}: {str(e)}")
            return None

    def get_video_transcript(self, video_id: str) -> Optional[List[Dict]]:
        """
        Fetch video transcript using YouTube Transcript API
        """
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return transcript
        except Exception as e:
            print(f"Error fetching transcript for {video_id}: {str(e)}")
            return None

    def save_video_data(self, video_id: str, data_dir: str = "data/raw"):
        """
        Save video details and transcript to JSON files
        """
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Get video details
        video_details = self.get_video_details(video_id)
        if video_details:
            # Save video details
            details_file = os.path.join(data_dir, f"{video_id}_details.json")
            with open(details_file, 'w', encoding='utf-8') as f:
                json.dump(video_details, f, ensure_ascii=False, indent=2)
            
            # Get and save transcript
            transcript = self.get_video_transcript(video_id)
            if transcript:
                transcript_file = os.path.join(data_dir, f"{video_id}_transcript.json")
                with open(transcript_file, 'w', encoding='utf-8') as f:
                    json.dump(transcript, f, ensure_ascii=False, indent=2)
            
            return True
        return False
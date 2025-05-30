from typing import Dict, Optional
import xml.etree.ElementTree as ET
from datetime import datetime
import json
import os
from .youtube_api import YouTubeAPI

class DataCollector:
    def __init__(self):
        self.youtube_api = YouTubeAPI()
        self.raw_data_dir = "data/raw"
        self.processed_data_dir = "data/processed"
        
        # Ensure directories exist
        os.makedirs(self.raw_data_dir, exist_ok=True)
        os.makedirs(self.processed_data_dir, exist_ok=True)

    def process_notification(self, notification_data: bytes) -> Optional[str]:
        """
        Process incoming notification from PubSubHubbub
        Returns video ID if successfully processed, None otherwise
        """
        try:
            # Parse XML content
            root = ET.fromstring(notification_data)
            
            # Find video ID from the feed
            # XML namespace for Atom feed
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            # Extract video ID from entry link
            entry = root.find('atom:entry', ns)
            if entry is None:
                return None
                
            video_link = entry.find('atom:link', ns)
            if video_link is None:
                return None
                
            # Extract video ID from link
            video_url = video_link.get('href', '')
            video_id = video_url.split('watch?v=')[-1]
            
            if video_id:
                # Collect and save video data
                self.youtube_api.save_video_data(video_id)
                return video_id
            
            return None
            
        except Exception as e:
            print(f"Error processing notification: {str(e)}")
            return None

    def process_video_data(self, video_id: str) -> bool:
        """
        Process collected video data to determine sponsorship
        """
        try:
            # Read the collected data
            details_file = os.path.join(self.raw_data_dir, f"{video_id}_details.json")
            transcript_file = os.path.join(self.raw_data_dir, f"{video_id}_transcript.json")
            
            if not os.path.exists(details_file):
                return False
                
            with open(details_file, 'r', encoding='utf-8') as f:
                video_details = json.load(f)
                
            transcript = None
            if os.path.exists(transcript_file):
                with open(transcript_file, 'r', encoding='utf-8') as f:
                    transcript = json.load(f)
            
            # Combine data into a single processed record
            processed_data = {
                'video_id': video_id,
                'processed_at': datetime.utcnow().isoformat(),
                'video_details': video_details,
                'transcript': transcript
            }
            
            # Save processed data
            output_file = os.path.join(self.processed_data_dir, f"{video_id}_processed.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, ensure_ascii=False, indent=2)
                
            return True
            
        except Exception as e:
            print(f"Error processing video data for {video_id}: {str(e)}")
            return False
import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class YouTube:
    def __init__(self):
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Please set YOUTUBE_API_KEY in your .env file.")
        self.base_url = "https://www.googleapis.com/youtube/v3/videos"

    def get_videos(self, publication_ids: str) -> dict:
        params = {
            "part": "snippet,statistics",
            "id": publication_ids,
            "key": self.api_key
        }
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        return response.json()

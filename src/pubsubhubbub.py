import os
import aiohttp
from typing import Optional
from urllib.parse import urljoin, urlparse

class PubSubHubbub:
    def __init__(self):
        self.hub_url = "https://pubsubhubbub.appspot.com/subscribe"
        default_callback = "http://localhost:8000/webhook"  # More sensible default
        self.callback_url = os.getenv("CALLBACK_URL", default_callback)
        self.verify_token = os.getenv("WEBHOOK_VERIFY_TOKEN")
        
        # Validate callback URL
        if not self._is_valid_url(self.callback_url):
            raise ValueError(f"Invalid callback URL: {self.callback_url}")

    def _is_valid_url(self, url: str) -> bool:
        """Validate if the given URL is properly formatted."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    async def subscribe_to_channel(self, channel_id: str) -> bool:
        """
        Subscribe to a YouTube channel's updates
        """
        topic_url = f"https://www.youtube.com/xml/feeds/videos.xml?channel_id={channel_id}"
        
        async with aiohttp.ClientSession() as session:
            try:
                response = await session.post(
                    self.hub_url,
                    data={
                        "hub.callback": self.callback_url,
                        "hub.topic": topic_url,
                        "hub.verify": "sync",
                        "hub.mode": "subscribe",
                        "hub.verify_token": self.verify_token
                    }
                )
                return response.status == 202
            except Exception as e:
                print(f"Error subscribing to channel {channel_id}: {str(e)}")
                return False

    async def unsubscribe_from_channel(self, channel_id: str) -> bool:
        """
        Unsubscribe from a YouTube channel's updates
        """
        topic_url = f"https://www.youtube.com/xml/feeds/videos.xml?channel_id={channel_id}"
        
        async with aiohttp.ClientSession() as session:
            try:
                response = await session.post(
                    self.hub_url,
                    data={
                        "hub.callback": self.callback_url,
                        "hub.topic": topic_url,
                        "hub.verify": "sync",
                        "hub.mode": "unsubscribe",
                        "hub.verify_token": self.verify_token
                    }
                )
                return response.status == 202
            except Exception as e:
                print(f"Error unsubscribing from channel {channel_id}: {str(e)}")
                return False

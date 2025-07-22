import os
import aiohttp
import logging
import asyncio
from typing import Optional, Dict, Any
from urllib.parse import urljoin, urlparse, urlunparse

# Configure logging
logger = logging.getLogger(__name__)

class PubSubHubbubError(Exception):
    """Custom exception for PubSubHubbub related errors."""
    pass

class PubSubHubbub:
    """Handles PubSubHubbub subscriptions for YouTube channel updates."""
    
    def __init__(self):
        """Initialize the PubSubHubbub client with configuration from environment variables."""
        self.hub_url = "https://pubsubhubbub.appspot.com/subscribe"
        
        # Set default callback URL with HTTPS
        default_callback = "https://localhost:8000/webhook"
        self.callback_url = os.getenv("CALLBACK_URL", default_callback)
        
        # Ensure callback URL ends with /webhook
        if not self.callback_url.endswith('/webhook'):
            self.callback_url = self.callback_url.rstrip('/') + '/webhook'
        
        # Validate and normalize the callback URL
        self.callback_url = self._normalize_url(self.callback_url)
        
        # Get verification token
        self.verify_token = os.getenv("WEBHOOK_VERIFY_TOKEN")
        
        if not self.verify_token:
            logger.warning("WEBHOOK_VERIFY_TOKEN is not set in environment variables")

    def _normalize_url(self, url: str) -> str:
        """Normalize and validate the URL, ensuring it uses HTTPS."""
        try:
            parsed = urlparse(url)
            if not all([parsed.scheme, parsed.netloc]):
                raise ValueError("URL must include scheme and netloc")
                
            # Force HTTPS
            if parsed.scheme != 'https':
                parsed = parsed._replace(scheme='https')
                logger.warning(f"URL scheme forced to HTTPS: {url}")
                
            # Reconstruct URL
            normalized_url = urlunparse(parsed)
            return normalized_url
            
        except Exception as e:
            logger.error(f"Invalid URL format: {url}")
            raise PubSubHubbubError(f"Invalid URL format: {str(e)}")

    async def _make_hub_request(self, channel_id: str, mode: str) -> bool:
        """
        Make a request to the PubSubHubbub hub with improved error handling.
        
        Args:
            channel_id: YouTube channel ID to subscribe to
            mode: 'subscribe' or 'unsubscribe'
            
        Returns:
            bool: True if successful, False otherwise
        """
        if mode not in ('subscribe', 'unsubscribe'):
            raise ValueError("Mode must be either 'subscribe' or 'unsubscribe'")
            
        topic_url = f"https://www.youtube.com/xml/feeds/videos.xml?channel_id={channel_id}"
        
        data = {
            "hub.callback": self.callback_url,
            "hub.topic": topic_url,
            "hub.verify": "sync",
            "hub.mode": mode,
            "hub.lease_seconds": "864000"  # 10 days
        }
        
        # Add verify token if available
        if self.verify_token:
            data["hub.verify_token"] = self.verify_token
        
        logger.info(f"PubSubHubbub {mode} request for channel {channel_id}")
        logger.debug(f"Request data: {data}")
        
        try:
            async with aiohttp.ClientSession() as session:
                # First try with a short timeout
                try:
                    async with session.post(
                        self.hub_url,
                        data=data,
                        timeout=30,
                        headers={'User-Agent': 'Mozilla/5.0'}
                    ) as response:
                        response_text = await response.text()
                        logger.info(f"Response status: {response.status}")
                        logger.debug(f"Response text: {response_text}")

                        # Check for successful response
                        if response.status in (202, 204):
                            logger.info(f"Successfully sent {mode} request for channel {channel_id}")
                            return True

                        # Handle conflict (409) - subscription already exists
                        if response.status == 409 and "already subscribed" in response_text.lower():
                            logger.info(f"Channel {channel_id} is already {mode}d")
                            return True

                        logger.error(
                            f"Failed to {mode} channel {channel_id}. "
                            f"Status: {response.status}, Response: {response_text}"
                        )
                        return False

                except asyncio.TimeoutError:
                    logger.error(f"Timeout while trying to {mode} channel {channel_id}")
                    return False
                    
        except Exception as e:
            logger.exception(f"Unexpected error during {mode} for channel {channel_id}")
            return False

    async def subscribe_to_channel(self, channel_id: str) -> bool:
        """
        Subscribe to a YouTube channel's updates.
        
        Args:
            channel_id: The YouTube channel ID to subscribe to
            
        Returns:
            bool: True if subscription request was successful, False otherwise
        """
        if not channel_id or not isinstance(channel_id, str):
            logger.error("Invalid channel_id provided")
            return False
            
        return await self._make_hub_request(channel_id, 'subscribe')

    async def unsubscribe_from_channel(self, channel_id: str) -> bool:
        """
        Unsubscribe from a YouTube channel's updates.
        
        Args:
            channel_id: The YouTube channel ID to unsubscribe from
            
        Returns:
            bool: True if unsubscription request was successful, False otherwise
        """
        if not channel_id or not isinstance(channel_id, str):
            logger.error("Invalid channel_id provided")
            return False
            
        return await self._make_hub_request(channel_id, 'unsubscribe')

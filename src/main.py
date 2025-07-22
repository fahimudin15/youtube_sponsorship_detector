from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import hashlib
import hmac
import os
import json
import time
from dotenv import load_dotenv
from .data_collector import DataCollector
from .analyzer import VideoAnalyzer
from .pubsubhubbub import PubSubHubbub
import logging
from pathlib import Path
from datetime import datetime

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(title="YouTube Sponsorship Detector")

# Setup data collector and analyzer
data_collector = DataCollector()
video_analyzer = VideoAnalyzer(model_path=os.getenv('MODEL_PATH'))

# In-memory notification log
notifications = []

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join('data', 'processed', 'app.log'))
    ]
)
logger = logging.getLogger(__name__)

# Pydantic models
class YouTubeNotification(BaseModel):
    feed: str
    video_id: str = None

class AnalysisResponse(BaseModel):
    video_id: str
    status: str
    analyzed_at: str
    threshold: float
    sponsored_regions: list
    segments: list

# Ensure processed directory exists
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/")
async def root():
    return {"status": "alive"}

@app.get("/webhook")
async def webhook_verification(request: Request):
    """
    Handle the webhook verification from PubSubHubbub
    """
    try:
        params = dict(request.query_params)
        logger.info(f"Received verification request: {params}")

        if params.get('hub.mode') in ['subscribe', 'unsubscribe']:
            verify_token = os.getenv('WEBHOOK_VERIFY_TOKEN')
            if params.get('hub.verify_token') == verify_token:
                challenge = params.get('hub.challenge')
                logger.info(f"Verification successful for mode {params.get('hub.mode')}")
                return Response(content=challenge, media_type="text/plain")
            else:
                logger.error(f"Invalid verify token. Expected: {verify_token}, Got: {params.get('hub.verify_token')}")

        logger.warning(f"Verification failed. Mode: {params.get('hub.mode')}")
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.exception("Error in webhook verification:")
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.post("/webhook")
async def webhook_receiver(request: Request):
    """
    Handle incoming notifications from YouTube and save as XML
    """
    try:
        # Get raw body
        body = await request.body()
        headers = dict(request.headers)
        signature = headers.get('X-Hub-Signature')

        logger.info(f"Received webhook notification. Headers: {headers}")

        # Signature verification
        if os.getenv('WEBHOOK_SECRET'):
            if not signature:
                logger.warning("No signature provided but WEBHOOK_SECRET is set")
                return Response(status_code=status.HTTP_403_FORBIDDEN)

            expected_sig = hmac.new(
                os.getenv('WEBHOOK_SECRET').encode(),
                body,
                hashlib.sha1
            ).hexdigest()

            if signature != f"sha1={expected_sig}":
                logger.warning(f"Invalid signature received: {signature}")
                return Response(status_code=status.HTTP_403_FORBIDDEN)

        # Parse XML
        try:
            from xml.etree import ElementTree
            xml_data = body.decode()
            ElementTree.fromstring(xml_data)
            logger.debug("Successfully parsed XML notification")
        except Exception as e:
            logger.error(f"Invalid XML received: {str(e)}")
            return Response(status_code=status.HTTP_400_BAD_REQUEST)

        # Store in memory
        notifications.append((str(headers), xml_data, str(datetime.now())))
        notifications[:] = notifications[-10:]

        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"youtube_notification_{timestamp}.xml"
        filepath = PROCESSED_DIR / filename

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(xml_data)
            logger.info(f"Saved notification to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save notification to {filepath}: {str(e)}")

        # Process video
        video_id = data_collector.process_notification(body)
        if video_id:
            logger.info(f"Processing new video: {video_id}")
            try:
                data_collector.process_video_data(video_id)
                logger.info(f"Successfully processed video {video_id}")
            except Exception as e:
                logger.error(f"Error processing video {video_id}: {str(e)}")
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={"error": f"Error processing video: {str(e)}"}
                )
        else:
            logger.warning("No video ID found in notification")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "No video ID found in notification"}
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "success", "video_id": video_id}
        )

    except Exception as e:
        logger.exception("Error processing webhook notification:")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Internal server error"}
        )

@app.post("/analyze/{video_id}")
async def analyze_video(video_id: str, threshold: float = 0.5):
    try:
        logger.info(f"Received analysis request for video_id={video_id}, threshold={threshold}")
        if not data_collector.process_video_data(video_id):
            logger.error(f"Failed to collect video data for {video_id}")
            return {"status": "error", "message": "Failed to collect video data"}
        results = video_analyzer.analyze_video(video_id, threshold)
        video_analyzer.save_results(results)
        logger.info(f"Analysis complete for video_id={video_id}")
        return results
    except Exception as e:
        logger.exception(f"Error analyzing video {video_id}")
        return {"status": "error", "message": str(e)}

@app.post("/subscribe/{channel_id}")
async def subscribe_channel(channel_id: str):
    """
    Subscribe to a YouTube channel's PubSubHubbub notifications.
    """
    required_vars = ["CALLBACK_URL", "WEBHOOK_VERIFY_TOKEN"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
        logger.error(error_msg)
        return {"status": "error", "message": error_msg}

    logger.info(f"CALLBACK_URL: {os.getenv('CALLBACK_URL')}")
    logger.info(f"WEBHOOK_VERIFY_TOKEN: {'*' * 8}{os.getenv('WEBHOOK_VERIFY_TOKEN')[-4:] if os.getenv('WEBHOOK_VERIFY_TOKEN') else 'None'}")

    pubsub = PubSubHubbub()
    try:
        result = await pubsub.subscribe_to_channel(channel_id)
        if result:
            return {"status": "success", "message": f"Subscribed to channel {channel_id}"}
        else:
            return {"status": "error", "message": f"Failed to subscribe to channel {channel_id}"}
    except Exception as e:
        logger.exception(f"Error subscribing to channel {channel_id}")
        return {"status": "error", "message": str(e)}

@app.post("/unsubscribe/{channel_id}")
async def unsubscribe_channel(channel_id: str):
    """
    Unsubscribe from a YouTube channel's PubSubHubbub notifications.
    """
    pubsub = PubSubHubbub()
    try:
        result = await pubsub.unsubscribe_from_channel(channel_id)
        if result:
            return {"status": "success", "message": f"Unsubscribed from channel {channel_id}"}
        else:
            return {"status": "error", "message": f"Failed to unsubscribe from channel {channel_id}"}
    except Exception as e:
        logger.exception(f"Error unsubscribing from channel {channel_id}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

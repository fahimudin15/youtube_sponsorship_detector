from fastapi import FastAPI, Request, Response, status
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

load_dotenv()

app = FastAPI(title="YouTube Sponsorship Detector")
data_collector = DataCollector()
video_analyzer = VideoAnalyzer(model_path=os.getenv('MODEL_PATH'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join('data', 'processed', 'app.log'))
    ]
)
logger = logging.getLogger(__name__)

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

@app.get("/")
async def root():
    return {"status": "alive"}

@app.get("/webhook")
async def webhook_verification(request: Request):
    """
    Handle the webhook verification from PubSubHubbub
    This is called when initially setting up the subscription
    """
    params = dict(request.query_params)
    
    if params.get('hub.mode') == 'subscribe':
        if params.get('hub.verify_token') == os.getenv('WEBHOOK_VERIFY_TOKEN'):
            return Response(content=params.get('hub.challenge'), media_type="text/plain")
    
    return Response(status_code=status.HTTP_404_NOT_FOUND)

@app.post("/webhook")
async def webhook_receiver(request: Request):
    """
    Handle incoming notifications from YouTube
    """
    body = await request.body()
    signature = request.headers.get('X-Hub-Signature')
    
    # Log incoming webhook
    logger.info(f"Received webhook notification. Headers: {dict(request.headers)}")
    logger.info(f"Webhook body: {body.decode()}")
    
    # Verify the signature if provided
    if signature:
        expected_sig = hmac.new(
            os.getenv('WEBHOOK_SECRET').encode(),
            body,
            hashlib.sha1
        ).hexdigest()
        if signature != f"sha1={expected_sig}":
            logger.warning(f"Invalid signature received: {signature}")
            return Response(status_code=status.HTTP_403_FORBIDDEN)
    
    # Process the notification
    video_id = data_collector.process_notification(body)
    if video_id:
        logger.info(f"Processing new video: {video_id}")
        # Store notification in data directory
        notification_path = os.path.join('data', 'processed', f'notification_{video_id}_{int(time.time())}.json')
        os.makedirs(os.path.dirname(notification_path), exist_ok=True)
        with open(notification_path, 'w') as f:
            json.dump({
                'timestamp': time.time(),
                'video_id': video_id,
                'body': body.decode()
            }, f, indent=2)
        
        # Process the video data
        data_collector.process_video_data(video_id)
        logger.info(f"Successfully processed video {video_id}")
    else:
        logger.warning("Could not extract video_id from notification")
    
    return Response(status_code=status.HTTP_200_OK)

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
    pubsub = PubSubHubbub()
    try:
        result = await pubsub.subscribe_to_channel(channel_id)
        if result:
            return {"status": "success", "message": f"Subscribed to channel {channel_id}"}
        else:
            return {"status": "error", "message": f"Failed to subscribe to channel {channel_id}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

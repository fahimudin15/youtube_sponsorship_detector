import argparse
import sys
import os
import time
import logging
import asyncio
from analyzer import VideoAnalyzer
from data_collector import DataCollector
from pubsubhubbub import PubSubHubbub

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

def print_progress(message, end="\r"):
    print(message, end=end, flush=True)

def subscribe_channel(channel_id):
    pubsub = PubSubHubbub()
    async def run():
        result = await pubsub.subscribe_to_channel(channel_id)
        if result:
            print(f"[SUCCESS] Subscribed to channel {channel_id}.")
        else:
            print(f"[ERROR] Failed to subscribe to channel {channel_id}.")
    asyncio.run(run())

def unsubscribe_channel(channel_id):
    pubsub = PubSubHubbub()
    async def run():
        result = await pubsub.unsubscribe_from_channel(channel_id)
        if result:
            print(f"[SUCCESS] Unsubscribed from channel {channel_id}.")
        else:
            print(f"[ERROR] Failed to unsubscribe from channel {channel_id}.")
    asyncio.run(run())

def main():
    parser = argparse.ArgumentParser(description="YouTube Sponsorship Detector CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a YouTube video for sponsorship segments")
    analyze_parser.add_argument("video_id", type=str, help="YouTube video ID to analyze")
    analyze_parser.add_argument("--threshold", type=float, default=0.5, help="Confidence threshold for sponsorship detection (default: 0.5)")
    analyze_parser.add_argument("--model-path", type=str, default=None, help="Path to trained model directory")

    # Subscribe command
    subscribe_parser = subparsers.add_parser("subscribe", help="Subscribe to a YouTube channel for PubSubHubbub notifications")
    subscribe_parser.add_argument("channel_id", type=str, help="YouTube channel ID to subscribe")

    # Unsubscribe command
    unsubscribe_parser = subparsers.add_parser("unsubscribe", help="Unsubscribe from a YouTube channel for PubSubHubbub notifications")
    unsubscribe_parser.add_argument("channel_id", type=str, help="YouTube channel ID to unsubscribe")

    args = parser.parse_args()

    if args.command == "subscribe":
        subscribe_channel(args.channel_id)
        return
    elif args.command == "unsubscribe":
        unsubscribe_channel(args.channel_id)
        return
    elif args.command == "analyze":
        # Input validation
        if not args.video_id or len(args.video_id) < 5:
            print("[ERROR] Please provide a valid YouTube video ID.")
            sys.exit(1)
        if not (0.0 < args.threshold < 1.0):
            print("[ERROR] Threshold must be between 0 and 1.")
            sys.exit(1)
        if args.model_path and not os.path.exists(args.model_path):
            print(f"[ERROR] Model path '{args.model_path}' does not exist.")
            sys.exit(1)

        try:
            print_progress("[INFO] Initializing analyzer...        ")
            analyzer = VideoAnalyzer(model_path=args.model_path)
            collector = DataCollector()

            print_progress("[INFO] Collecting video data...      ")
            if not collector.process_video_data(args.video_id):
                logger.error("Failed to collect video data.")
                print("\n[ERROR] Failed to collect video data. Exiting.")
                sys.exit(1)

            print_progress("[INFO] Analyzing video...            ")
            results = analyzer.analyze_video(args.video_id, args.threshold)
            print("\n[INFO] Analysis complete.")

            if results["status"] != "success":
                logger.error(f"Analysis failed: {results.get('message', 'Unknown error')}")
                print(f"[ERROR] {results.get('message', 'Unknown error')}")
                sys.exit(1)

            # Result visualization
            print(f"\n[RESULT] Sponsored Segments for Video ID: {args.video_id}")
            if not results["sponsored_regions"]:
                print("No sponsored segments detected.")
            else:
                for idx, region in enumerate(results["sponsored_regions"], 1):
                    print(f"  {idx}. Start: {region['start_time']}s, End: {region['end_time']}s, Confidence: {region['confidence']:.2f}")
            print(f"\n[INFO] Full analysis saved to: data/processed/{args.video_id}_analysis.json")
        except Exception as e:
            logger.exception("CLI error")
            print(f"[ERROR] {str(e)}")
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

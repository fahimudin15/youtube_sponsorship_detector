# User Guide: YouTube Sponsorship Detector

## Overview
This tool detects sponsorship segments in YouTube videos using a FastAPI backend and a command-line interface (CLI).

## Getting Started
1. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
2. **Configure `.env`** with your YouTube API key and webhook secrets.
3. **Start the FastAPI server:**
   ```sh
   uvicorn src.main:app --reload
   ```
4. **(Optional) Use the CLI:**
   ```sh
   python src/cli.py <video_id>
   ```

## FastAPI Endpoints
- `GET /` — Health check
- `GET /webhook` — Webhook verification
- `POST /webhook` — Receives YouTube notifications
- `POST /analyze/{video_id}` — Analyze a video for sponsorship segments

## CLI Usage
```sh
python src/cli.py <video_id> [--threshold 0.5] [--model-path path/to/model]
```

## Output
- Analysis results are saved in `data/processed/<video_id>_analysis.json`
- Sponsored segments are printed in the CLI and returned by the API

## Troubleshooting
- Ensure `.env` is configured
- Check logs for errors (both CLI and API log to console)
- For API errors, see the returned `message` field

## Deployment
- Use `deploy.ps1` for Windows deployment automation
- For production, use a process manager (e.g., Gunicorn, systemd, or Docker)

## CI/CD
- Add a `.github/workflows/python-app.yml` for GitHub Actions (see README for template)

## Support
For issues, open a GitHub issue or contact the maintainer.

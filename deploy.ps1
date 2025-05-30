# PowerShell deployment script for YouTube Sponsorship Detector
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set environment variables (edit .env as needed)
Write-Host "Ensure .env is configured with your API keys and secrets."

# 3. Run database migrations (if any)
# (No DB migrations required for current version)

# 4. Start FastAPI server
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# 5. (Optional) Run CLI for a test video
# python src/cli.py <video_id>

Write-Host "Deployment complete. Visit http://localhost:8000/docs for API documentation."

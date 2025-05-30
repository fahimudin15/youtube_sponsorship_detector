# YouTube Sponsorship Detector

A FastAPI-based system for detecting sponsorship segments in YouTube videos using machine learning.

## Installation

1. **Clone the repository**
2. **Set up a Python virtual environment**
3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Configure environment variables:**
   - Copy `.env` and fill in your YouTube API key and webhook secrets.

## Usage

### FastAPI Server
Start the API server:
```sh
uvicorn src.main:app --reload
```

- Webhook endpoint: `/webhook` (GET for verification, POST for notifications)
- Analyze video: `POST /analyze/{video_id}`

### Command-Line Interface (CLI)
Analyze a video from the command line:
```sh
python src/cli.py <video_id> [--threshold 0.5] [--model-path path/to/model]
```

## API Documentation

### POST /analyze/{video_id}
- **Description:** Analyze a YouTube video for sponsorship segments.
- **Parameters:**
  - `video_id` (path): YouTube video ID
  - `threshold` (query, optional): Confidence threshold (default: 0.5)
- **Response:**
  - `status`: success/error
  - `sponsored_regions`: List of detected sponsored segments with start/end times and confidence
  - `segments`: All analyzed segments

### GET /webhook
- **Description:** Webhook verification endpoint for PubSubHubbub

### POST /webhook
- **Description:** Receives notifications for new videos

## Model Architecture & Training
- Uses DistilBERT for text classification
- Data is preprocessed and tokenized using HuggingFace Transformers
- Model is trained to classify transcript segments as sponsored or not
- Training and evaluation handled in `src/model.py`
- Model versioning and saving supported

## Project Structure
- `src/` - Source code (API, CLI, model, data processing)
- `data/` - Raw and processed video data
- `models/` - Saved model checkpoints
- `tests/` - Unit and integration tests

## Deployment
- Use `deploy.ps1` for Windows deployment automation
- For production, use a process manager (e.g., Gunicorn, systemd, or Docker)

## CI/CD Example (GitHub Actions)
Create `.github/workflows/python-app.yml`:
```yaml
name: Python application
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run tests
      run: pytest tests/
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first.

## License
MIT

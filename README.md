# YouTube Sponsorship Detector

This project is designed to detect sponsorships in YouTube video descriptions. It uses the YouTube Data API to fetch video details and processes the descriptions to identify sponsorships.

## Project Structure

- `app.py`: Contains the Flask application with endpoints for detecting publications and confirming channel subscriptions.
- `youtube.py`: Contains the `YouTubeAPI` class for interacting with the YouTube Data API.
- `dataclass/Publication.py`: Contains the `Publication` data class for handling YouTube publication data.
- `dataclass/detector.py`: Contains the `YoutubeSponsorshipDetector` class for processing and detecting sponsorships.
- `pages/`: Contains the Next.js frontend application.
- `VideoForm.js`: Contains the React component for the video URL submission form.
- `pages/api/check-sponsorship.js`: Contains the API endpoint for checking sponsorships in video descriptions.

## Setup

1. Clone the repository:
    ```bash
    git clone https://github.com/fahimudin15/youtube_sponsorship_detector.git
    cd youtube_sponsorship_detector
    ```

2. Create a virtual environment and activate it:
    ```bash
    python -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Create a `.env` file  and set your YouTube API key:
    

5. Set your YouTube API key in the `.env` file:
    ```dotenv
    YOUTUBE_API_KEY=your_youtube_api_key_here
    ```

Replace `your_youtube_api_key_here` with your actual YouTube API key.

## Running the Project

6. Navigate to the project directory:
    ```bash
    cd youtube_sponsorship_detector
    ```

7. Install the required dependencies:
    ```bash
    npm install
    ```

8. Start the Next.js development server:
    ```bash
    npm run dev
    ```

9. The frontend application will be available at `http://localhost:3000`.

## Endpoints

- `GET /`: Home endpoint that triggers the `YoutubeSponsorshipDetector`.
- `GET /channels`: Endpoint to confirm channel subscription.
- `POST /channels`: Endpoint to detect publication and process the description.
- `GET /youtube-publications`: Endpoint to fetch YouTube video details by publication IDs.
- `POST /api/check-sponsorship`: API endpoint to check for sponsorships in video descriptions.

## Example Usage

To detect sponsorships in a YouTube video description, send a POST request to the `/channels` endpoint with the XML data of the publication.

```bash
curl -X POST http://127.0.0.1:5000/channels -d @publication.xml
```

## License

This project is licensed under the MIT License.

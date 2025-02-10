import axios from 'axios';
import fs from 'fs';
import path from 'path';
import yaml from 'js-yaml';

// Load sponsorship keywords from agents.yaml
let sponsorshipKeywords = [];
try {
  const configPath = path.join(process.cwd(), 'agents', 'detector', 'config', 'agents.yaml');
  const config = yaml.load(fs.readFileSync(configPath, 'utf8'));
  sponsorshipKeywords = config.sponsorship_keywords;
  if (!Array.isArray(sponsorshipKeywords)) {
    throw new Error('Invalid sponsorship keywords format');
  }
  console.log('Loaded sponsorship keywords:', sponsorshipKeywords);
} catch (error) {
  console.error('Error loading sponsorship keywords:', error.message);
}

export default async function handler(req, res) {
  if (req.method === 'POST') {
    const { videoUrl } = req.body;
    console.log('Received video URL:', videoUrl);

    // Extract the video ID from the URL
    const videoIdMatch = videoUrl.match(/(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^&]+)/);
    if (!videoIdMatch) {
      console.error('Invalid video URL');
      return res.status(400).json({ error: 'Invalid video URL' });
    }

    const videoId = videoIdMatch[1];
    console.log('Extracted video ID:', videoId);

    try {
      // Replace 'YOUR_API_KEY' with your actual YouTube Data API key
      const response = await axios.get(`https://www.googleapis.com/youtube/v3/videos?id=${videoId}&key=AIzaSyCQfCbiZO3zXbsgxOef_jmLj0BhuRAbbkE&part=snippet`);
      console.log('API response:', response.data);

      if (response.data.items.length === 0) {
        throw new Error('No video details found');
      }

      const videoDetails = response.data.items[0].snippet;
      const sponsorshipDetected = detectSponsorship(videoDetails.description);

      res.status(200).json({ sponsorshipDetected });
    } catch (error) {
      console.error('Error fetching video details:', error.message);
      res.status(500).json({ error: 'Failed to fetch video details', details: error.message });
    }
  } else {
    res.status(405).json({ error: 'Method not allowed' });
  }
}

function detectSponsorship(description) {
  console.log('Checking description for sponsorship:', description);
  const lowerCaseDescription = description.toLowerCase();
  return sponsorshipKeywords.some(keyword => lowerCaseDescription.includes(keyword));
}
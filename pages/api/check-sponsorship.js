import axios from 'axios';
import fs from 'fs';
import path from 'path';
import yaml from 'js-yaml';

// Load sponsorship keywords from agents.yaml
let sponsorshipKeywords = [];
try {
  const configPath = path.join(process.cwd(), 'agents', 'detector', 'config', 'agents.yaml');
  const config = yaml.load(fs.readFileSync(configPath, 'utf8'));

  if (config.sponsorship_detector && Array.isArray(config.sponsorship_detector.sponsorship_keywords)) {
    sponsorshipKeywords = config.sponsorship_detector.sponsorship_keywords.map(keyword => keyword.toLowerCase());
  } else {
    throw new Error('Invalid or missing sponsorship keywords');
  }

  console.log('Loaded sponsorship keywords:', sponsorshipKeywords);
} catch (error) {
  console.error('Error loading sponsorship keywords:', error.message);
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { videoUrl } = req.body;
  console.log('Received video URL:', videoUrl);

  // Extract video ID from URL
  const videoIdMatch = videoUrl.match(/(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^&]+)/);
  if (!videoIdMatch) {
    console.error('Invalid video URL');
    return res.status(400).json({ error: 'Invalid video URL' });
  }

  const videoId = videoIdMatch[1];
  console.log('Extracted video ID:', videoId);

  try {
    // Fetch video details
    const videoDetails = await fetchVideoDetails(videoId);
    if (!videoDetails || !videoDetails.description) {
      console.error('Video description not found');
      return res.status(500).json({ error: 'Video description not found' });
    }

    // Check for sponsorship
    const sponsorshipDetected = detectSponsorship(videoDetails.description);

    res.status(200).json({ sponsorshipDetected });
  } catch (error) {
    console.error('Error processing request:', error.message);
    res.status(500).json({ error: 'Failed to process request', details: error.message });
  }
}

// Function to fetch video details from YouTube API
async function fetchVideoDetails(videoId) {
  try {
    const apiKey = process.env.YOUTUBE_API_KEY; // Set this in your .env file
    const url = `https://www.googleapis.com/youtube/v3/videos?id=${videoId}&part=snippet&key=${apiKey}`;
    const response = await axios.get(
      `https://www.googleapis.com/youtube/v3/videos?id=${videoId}&key=AIzaSyCQfCbiZO3zXbsgxOef_jmLj0BhuRAbbkE
&part=snippet`
    );
    
    if (!response.data.items.length) {
      throw new Error('No video details found');
    }

    return response.data.items[0].snippet;
  } catch (error) {
    console.error('Error fetching video details:', error.message);
    return null;
  }
}

// Function to check if a description contains sponsorship
function detectSponsorship(description) {
  console.log('Checking description for sponsorship:', description);

  if (!description) {
    console.log('No description provided.');
    return false;
  }

  // Remove links, @mentions, and extra spaces
  const cleanedDescription = description
    .replace(/https?:\/\/\S+/g, '')  // Remove links
    .replace(/@\S+/g, '')  // Remove @mentions
    .replace(/\s+/g, ' ')  // Normalize spaces
    .trim();

  const lowerCaseDescription = cleanedDescription.toLowerCase();

  // Ensure sponsorship keywords are loaded
  if (!sponsorshipKeywords.length) {
    console.log('No sponsorship keywords loaded.');
    return false;
  }

  // Check if description contains any sponsorship keyword
  const sponsorshipDetected = sponsorshipKeywords.some(keyword =>
    lowerCaseDescription.includes(keyword)
  );

  console.log('Sponsorship detected:', sponsorshipDetected);
  return sponsorshipDetected;
}

import React, { useState } from 'react';
import axios from 'axios';

const VideoForm = () => {
  const [videoUrl, setVideoUrl] = useState('');
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('Submitting video URL:', videoUrl);

    try {
      const response = await axios.post('/api/check-sponsorship', { videoUrl });
      console.log('API response:', response.data);

      setResult(response.data.sponsorshipDetected ? 'Sponsorship detected' : 'No sponsorship detected');
    } catch (error) {
      console.error('Error checking sponsorship:', error.response ? error.response.data : error.message);
      setResult('Error checking sponsorship');
    }
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>YouTube Sponsorship Detector</h1>
      <form onSubmit={handleSubmit} style={styles.form}>
        <input
          type="text"
          value={videoUrl}
          onChange={(e) => setVideoUrl(e.target.value)}
          placeholder="Enter YouTube video URL"
          style={styles.input}
        />
        <button type="submit" style={styles.button}>Check Sponsorship</button>
      </form>
      {result && <p style={styles.result}>{result}</p>}
    </div>
  );
};

const styles = {
  container: {
    maxWidth: '600px',
    margin: '0 auto',
    padding: '20px',
    textAlign: 'center',
    fontFamily: 'Arial, sans-serif',
    backgroundColor: '#f0f8ff',
    borderRadius: '10px',
    boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
  },
  title: {
    fontSize: '24px',
    marginBottom: '20px',
    color: '#333',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  input: {
    width: '100%',
    padding: '10px',
    marginBottom: '10px',
    borderRadius: '5px',
    border: '1px solid #ccc',
    boxShadow: 'inset 0 1px 3px rgba(0, 0, 0, 0.1)',
  },
  button: {
    padding: '10px 20px',
    borderRadius: '5px',
    border: 'none',
    backgroundColor: '#007BFF',
    color: '#fff',
    cursor: 'pointer',
    transition: 'background-color 0.3s',
  },
  buttonHover: {
    backgroundColor: '#0056b3',
  },
  result: {
    marginTop: '20px',
    fontSize: '18px',
    color: '#333',
  },
};

export default VideoForm;
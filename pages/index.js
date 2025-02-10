import Head from 'next/head';
import VideoForm from '../VideoForm';

export default function Home() {
  return (
    <div style={styles.pageContainer}>
      <Head>
        <title>YouTube Sponsorship Detector</title>
        <meta name="description" content="Detect sponsorships in YouTube videos" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main style={styles.main}>
        <VideoForm />
      </main>
    </div>
  );
}

const styles = {
  pageContainer: {
    backgroundColor: '#e6f7ff', // Light blue background color for the page
    minHeight: '100vh', // Full viewport height
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    padding: '20px', // Add padding around the page
  },
  main: {
    width: '100%',
    maxWidth: '800px',
    padding: '20px',
    backgroundColor: '#ffffff', // White background for the main content
    boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)', // Add a subtle shadow
    borderRadius: '8px', // Rounded corners
  },
};

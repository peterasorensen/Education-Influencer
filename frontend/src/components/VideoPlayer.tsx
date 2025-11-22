import { toast } from 'sonner';

interface VideoPlayerProps {
  url: string;
  onNewVideo: () => void;
}

export const VideoPlayer = ({ url, onNewVideo }: VideoPlayerProps) => {
  const handleDownload = () => {
    toast.success('Download started!');
  };

  return (
    <div className="video-section">
      <h2 className="video-title">Your Video is Ready!</h2>
      <div className="video-wrapper">
        <video
          className="video-player"
          controls
          src={url}
          aria-label="Generated educational video"
        >
          Your browser does not support the video tag.
        </video>
      </div>
      <div className="action-buttons">
        <a
          href={url}
          download
          className="download-button"
          onClick={handleDownload}
          aria-label="Download video"
        >
          Download Video
        </a>
        <button
          onClick={onNewVideo}
          className="new-video-button"
          aria-label="Create another video"
        >
          Create Another Video
        </button>
      </div>
    </div>
  );
};

export default VideoPlayer;

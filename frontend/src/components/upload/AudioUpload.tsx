import { useRef, useState, type ChangeEvent } from 'react';
import { validateAudioFile, validateAudioDuration } from '../../services/mediaApi';
import type { AudioMetadata } from '../../types/media';

interface AudioUploadProps {
  onUpload: (file: File) => Promise<AudioMetadata>;
  uploadedAudio: AudioMetadata | null;
  isUploading: boolean;
  progress: number;
  error: string | null;
  onClear: () => void;
}

export const AudioUpload = ({
  onUpload,
  uploadedAudio,
  isUploading,
  progress,
  error,
  onClear,
}: AudioUploadProps) => {
  const [validationError, setValidationError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const audioRef = useRef<HTMLAudioElement>(null);

  const handleFileInput = async (e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const file = files[0];
    setValidationError(null);

    // Validate file type and size
    const typeValidation = validateAudioFile(file);
    if (typeValidation) {
      setValidationError(typeValidation);
      return;
    }

    // Validate duration
    const durationValidation = await validateAudioDuration(file);
    if (durationValidation) {
      setValidationError(durationValidation);
      return;
    }

    // Set selected file and upload
    setSelectedFile(file);
    try {
      await onUpload(file);
    } catch (err) {
      setSelectedFile(null);
    }
  };

  const handlePlayPreview = () => {
    if (!audioRef.current) return;

    if (isPlaying) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
    } else {
      audioRef.current.play();
      setIsPlaying(true);
    }
  };

  const handleAudioEnded = () => {
    setIsPlaying(false);
  };

  const handleClear = () => {
    setSelectedFile(null);
    setValidationError(null);
    setIsPlaying(false);
    onClear();
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="audio-upload">
      {!uploadedAudio && !isUploading && (
        <div className="upload-zone-audio" onClick={() => fileInputRef.current?.click()}>
          <div className="upload-icon">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"
              />
            </svg>
          </div>
          <p className="upload-text">
            <strong>Click to upload audio</strong>
          </p>
          <p className="upload-hint">MP3, WAV, WebM, or OGG (2-5 seconds, max 5MB)</p>
          <input
            ref={fileInputRef}
            type="file"
            accept="audio/mpeg,audio/mp3,audio/wav,audio/webm,audio/ogg"
            onChange={handleFileInput}
            style={{ display: 'none' }}
            aria-label="Upload audio file"
          />
        </div>
      )}

      {isUploading && (
        <div className="upload-progress-container">
          <div className="upload-status">
            <p className="upload-status-text">Uploading audio...</p>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${progress}%` }}></div>
            </div>
            <p className="progress-percentage">{progress}%</p>
          </div>
        </div>
      )}

      {uploadedAudio && (
        <div className="upload-complete">
          <div className="audio-preview">
            <div className="audio-icon-wrapper">
              <svg
                className="audio-icon"
                xmlns="http://www.w3.org/2000/svg"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"
                />
              </svg>
            </div>
            <button className="clear-button" onClick={handleClear} aria-label="Remove audio">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          <div className="upload-info">
            <p className="upload-filename">{uploadedAudio.filename}</p>
            <p className="upload-details">
              {uploadedAudio.duration_seconds.toFixed(1)}s •{' '}
              {(uploadedAudio.size_bytes / 1024).toFixed(1)} KB
            </p>
          </div>

          <div className="audio-player-controls">
            <button className="play-button" onClick={handlePlayPreview}>
              {isPlaying ? (
                <>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
                  </svg>
                  Pause
                </>
              ) : (
                <>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M8 5v14l11-7z" />
                  </svg>
                  Play
                </>
              )}
            </button>
          </div>

          <audio
            ref={audioRef}
            src={uploadedAudio.audio_url}
            onEnded={handleAudioEnded}
            style={{ display: 'none' }}
          />
        </div>
      )}

      {(error || validationError) && (
        <div className="upload-error">
          <svg
            className="error-icon"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
              clipRule="evenodd"
            />
          </svg>
          {error || validationError}
        </div>
      )}
    </div>
  );
};

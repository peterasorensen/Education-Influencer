import { useEffect, useRef, useState } from 'react';
import { useAudioRecorder } from '../../hooks/useAudioRecorder';
import type { AudioMetadata } from '../../types/media';

interface AudioRecorderProps {
  onUpload: (file: File) => Promise<AudioMetadata>;
  uploadedAudio: AudioMetadata | null;
  isUploading: boolean;
  progress: number;
  error: string | null;
  onClear: () => void;
}

export const AudioRecorder = ({
  onUpload,
  uploadedAudio,
  isUploading,
  progress,
  error,
  onClear,
}: AudioRecorderProps) => {
  const {
    isRecording,
    recordingTime,
    audioUrl,
    error: recorderError,
    permissionGranted,
    maxRecordingTime,
    requestPermission,
    startRecording,
    stopRecording,
    clearRecording,
    setWaveformCallback,
    getAudioFile,
  } = useAudioRecorder();

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);

  // Setup waveform visualization
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const drawWaveform = (dataArray: Uint8Array, bufferLength: number) => {
      const WIDTH = canvas.width;
      const HEIGHT = canvas.height;

      ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
      ctx.fillRect(0, 0, WIDTH, HEIGHT);

      ctx.lineWidth = 2;
      ctx.strokeStyle = '#4facfe';
      ctx.beginPath();

      const sliceWidth = (WIDTH * 1.0) / bufferLength;
      let x = 0;

      for (let i = 0; i < bufferLength; i++) {
        const v = dataArray[i] / 128.0;
        const y = (v * HEIGHT) / 2;

        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }

        x += sliceWidth;
      }

      ctx.lineTo(WIDTH, HEIGHT / 2);
      ctx.stroke();
    };

    setWaveformCallback((data) => {
      drawWaveform(data.dataArray, data.bufferLength);
    });
  }, [setWaveformCallback]);

  const handleStartRecording = async () => {
    if (!permissionGranted) {
      const granted = await requestPermission();
      if (!granted) return;
    }
    startRecording();
  };

  const handleUploadRecording = async () => {
    const file = getAudioFile();
    if (!file) return;

    try {
      await onUpload(file);
      clearRecording();
    } catch (err) {
      console.error('Upload failed:', err);
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

  const handleClearRecording = () => {
    clearRecording();
    setIsPlaying(false);
  };

  const handleClearUploaded = () => {
    onClear();
    setIsPlaying(false);
  };

  const formatTime = (seconds: number) => {
    return seconds.toFixed(1) + 's';
  };

  const timeRemaining = maxRecordingTime - recordingTime;
  const progressPercentage = (recordingTime / maxRecordingTime) * 100;

  return (
    <div className="audio-recorder">
      {!audioUrl && !isRecording && !uploadedAudio && !isUploading && (
        <div className="recorder-initial">
          <button
            className="record-button"
            onClick={handleStartRecording}
            aria-label="Start recording"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
              <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
            </svg>
            <span>Record Audio</span>
          </button>
          <p className="recorder-hint">Record a 2-5 second audio clip</p>
        </div>
      )}

      {isRecording && (
        <div className="recording-active">
          <div className="recording-header">
            <div className="recording-indicator">
              <span className="recording-dot"></span>
              <span className="recording-text">Recording</span>
            </div>
            <div className="recording-timer">
              {formatTime(timeRemaining)} remaining
            </div>
          </div>

          <canvas
            ref={canvasRef}
            className="waveform-canvas"
            width={600}
            height={120}
            aria-label="Audio waveform visualization"
          />

          <div className="recording-progress">
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${progressPercentage}%` }}></div>
            </div>
          </div>

          <button className="stop-button" onClick={stopRecording}>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <rect x="6" y="6" width="12" height="12" rx="2" />
            </svg>
            Stop Recording
          </button>
        </div>
      )}

      {audioUrl && !uploadedAudio && !isUploading && (
        <div className="recording-complete">
          <div className="preview-header">
            <svg
              className="preview-icon"
              xmlns="http://www.w3.org/2000/svg"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
              <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
            </svg>
            <span>Recording complete ({formatTime(recordingTime)})</span>
          </div>

          <div className="preview-controls">
            <button className="preview-button" onClick={handlePlayPreview}>
              {isPlaying ? (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
                </svg>
              ) : (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M8 5v14l11-7z" />
                </svg>
              )}
              {isPlaying ? 'Pause' : 'Play Preview'}
            </button>

            <button className="rerecord-button" onClick={handleClearRecording}>
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
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
              Re-record
            </button>

            <button className="upload-button" onClick={handleUploadRecording}>
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
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
              </svg>
              Upload
            </button>
          </div>

          <audio
            ref={audioRef}
            src={audioUrl}
            onEnded={handleAudioEnded}
            style={{ display: 'none' }}
          />
        </div>
      )}

      {isUploading && (
        <div className="upload-progress-container">
          <p className="upload-status-text">Uploading audio...</p>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${progress}%` }}></div>
          </div>
          <p className="progress-percentage">{progress}%</p>
        </div>
      )}

      {uploadedAudio && (
        <div className="upload-complete">
          <div className="audio-preview">
            <svg
              className="audio-icon"
              xmlns="http://www.w3.org/2000/svg"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
              <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
            </svg>
            <button className="clear-button" onClick={handleClearUploaded} aria-label="Remove audio">
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
        </div>
      )}

      {(error || recorderError) && (
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
          {error || recorderError}
        </div>
      )}
    </div>
  );
};

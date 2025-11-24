import { useState } from 'react';
import { PhotoUpload } from '../upload/PhotoUpload';
import { AudioRecorder } from '../upload/AudioRecorder';
import { AudioUpload } from '../upload/AudioUpload';
import { useMediaUpload } from '../../hooks/useMediaUpload';

type AudioMode = 'record' | 'upload';

interface CustomCelebrityProps {
  photoId?: string;
  audioId?: string;
  onPhotoUpload: (photoId: string) => void;
  onAudioUpload: (audioId: string) => void;
}

export const CustomCelebrity = ({ photoId: _photoId, audioId: _audioId, onPhotoUpload, onAudioUpload }: CustomCelebrityProps) => {
  const [audioMode, setAudioMode] = useState<AudioMode>('record');
  const {
    photoState,
    uploadedPhoto,
    uploadPhoto,
    clearPhoto,
    audioState,
    uploadedAudio,
    uploadAudio,
    clearAudio,
  } = useMediaUpload();

  const handlePhotoUploadSuccess = async (file: File) => {
    const metadata = await uploadPhoto(file);
    onPhotoUpload(metadata.photo_id);
    return metadata;
  };

  const handleAudioUploadSuccess = async (file: File) => {
    const metadata = await uploadAudio(file);
    onAudioUpload(metadata.audio_id);
    return metadata;
  };

  return (
    <div className="custom-celebrity">
      <div className="custom-section">
        <h3 className="section-title">Upload Your Photo</h3>
        <p className="section-description">
          Upload a clear photo of yourself or anyone you'd like to feature in the video
        </p>
        <PhotoUpload
          onUpload={handlePhotoUploadSuccess}
          uploadedPhoto={uploadedPhoto}
          isUploading={photoState.isUploading}
          progress={photoState.progress}
          error={photoState.error}
          onClear={clearPhoto}
        />
      </div>

      <div className="custom-section">
        <h3 className="section-title">Add Your Voice</h3>
        <p className="section-description">
          Record or upload a 2-5 second audio clip (optional but recommended)
        </p>

        <div className="audio-mode-selector">
          <button
            className={`mode-button ${audioMode === 'record' ? 'active' : ''}`}
            onClick={() => setAudioMode('record')}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
              <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
            </svg>
            Record
          </button>
          <button
            className={`mode-button ${audioMode === 'upload' ? 'active' : ''}`}
            onClick={() => setAudioMode('upload')}
          >
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
            Upload
          </button>
        </div>

        {audioMode === 'record' ? (
          <AudioRecorder
            onUpload={handleAudioUploadSuccess}
            uploadedAudio={uploadedAudio}
            isUploading={audioState.isUploading}
            progress={audioState.progress}
            error={audioState.error}
            onClear={clearAudio}
          />
        ) : (
          <AudioUpload
            onUpload={handleAudioUploadSuccess}
            uploadedAudio={uploadedAudio}
            isUploading={audioState.isUploading}
            progress={audioState.progress}
            error={audioState.error}
            onClear={clearAudio}
          />
        )}
      </div>

      {uploadedPhoto && (
        <div className="custom-summary">
          <div className="summary-header">
            <svg
              className="success-icon"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clipRule="evenodd"
              />
            </svg>
            <span>Custom celebrity ready!</span>
          </div>
          <p className="summary-text">
            Your photo{uploadedAudio ? ' and audio' : ''} will be used to create your personalized
            video narrator
          </p>
        </div>
      )}
    </div>
  );
};

import { useState, useRef, type DragEvent, type ChangeEvent } from 'react';
import { validatePhotoFile } from '../../services/mediaApi';
import type { PhotoMetadata } from '../../types/media';

interface PhotoUploadProps {
  onUpload: (file: File) => Promise<PhotoMetadata>;
  uploadedPhoto: PhotoMetadata | null;
  isUploading: boolean;
  progress: number;
  error: string | null;
  onClear: () => void;
}

export const PhotoUpload = ({
  onUpload,
  uploadedPhoto,
  isUploading,
  progress,
  error,
  onClear,
}: PhotoUploadProps) => {
  const [isDragging, setIsDragging] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    setValidationError(null);

    // Validate file
    const validationMessage = validatePhotoFile(file);
    if (validationMessage) {
      setValidationError(validationMessage);
      return;
    }

    // Create preview
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);

    // Validate dimensions
    const img = new Image();
    img.onload = async () => {
      URL.revokeObjectURL(url);

      if (img.width < 256 || img.height < 256) {
        setValidationError('Photo must be at least 256x256 pixels');
        setPreviewUrl(null);
        return;
      }

      // Upload file
      try {
        await onUpload(file);
      } catch (err) {
        setPreviewUrl(null);
      }
    };

    img.onerror = () => {
      URL.revokeObjectURL(url);
      setValidationError('Could not load image');
      setPreviewUrl(null);
    };

    img.src = url;
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFileInput = (e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleClear = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
    }
    setValidationError(null);
    onClear();
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="photo-upload">
      {!uploadedPhoto && !isUploading && (
        <div
          className={`upload-zone ${isDragging ? 'dragging' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
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
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
          </div>
          <p className="upload-text">
            <strong>Click to upload</strong> or drag and drop
          </p>
          <p className="upload-hint">JPEG, PNG, or WebP (min 256x256, max 10MB)</p>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            onChange={handleFileInput}
            style={{ display: 'none' }}
            aria-label="Upload photo"
          />
        </div>
      )}

      {isUploading && (
        <div className="upload-progress-container">
          <div className="upload-preview">
            {previewUrl && <img src={previewUrl} alt="Uploading" />}
          </div>
          <div className="upload-status">
            <p className="upload-status-text">Uploading photo...</p>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${progress}%` }}></div>
            </div>
            <p className="progress-percentage">{progress}%</p>
          </div>
        </div>
      )}

      {uploadedPhoto && (
        <div className="upload-complete">
          <div className="photo-preview">
            <img src={uploadedPhoto.photo_url} alt="Uploaded" />
            <div className="photo-overlay">
              <button
                className="clear-button"
                onClick={handleClear}
                aria-label="Remove photo"
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
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>
          </div>
          <div className="upload-info">
            <p className="upload-filename">{uploadedPhoto.filename}</p>
            <p className="upload-details">
              {uploadedPhoto.dimensions.width} x {uploadedPhoto.dimensions.height} •{' '}
              {(uploadedPhoto.size_bytes / 1024).toFixed(1)} KB
            </p>
          </div>
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

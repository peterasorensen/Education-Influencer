// Media API Service for uploading and managing custom celebrity media

import type { PhotoMetadata, AudioMetadata, UserMedia } from '../types/media';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const uploadPhoto = async (
  file: File,
  userId?: string,
  onProgress?: (progress: number) => void
): Promise<PhotoMetadata> => {
  const formData = new FormData();
  formData.append('file', file);
  if (userId) {
    formData.append('user_id', userId);
  }

  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();

    // Track upload progress
    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable && onProgress) {
        const progress = Math.round((e.loaded / e.total) * 100);
        onProgress(progress);
      }
    });

    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const data = JSON.parse(xhr.responseText);
          resolve(data);
        } catch (error) {
          reject(new Error('Failed to parse server response'));
        }
      } else {
        try {
          const error = JSON.parse(xhr.responseText);
          reject(new Error(error.detail || `Upload failed with status ${xhr.status}`));
        } catch {
          reject(new Error(`Upload failed with status ${xhr.status}`));
        }
      }
    });

    xhr.addEventListener('error', () => {
      reject(new Error('Network error during upload'));
    });

    xhr.addEventListener('abort', () => {
      reject(new Error('Upload cancelled'));
    });

    xhr.open('POST', `${API_URL}/api/media/photo`);
    xhr.send(formData);
  });
};

export const uploadAudio = async (
  file: File,
  userId?: string,
  onProgress?: (progress: number) => void
): Promise<AudioMetadata> => {
  const formData = new FormData();
  formData.append('file', file);
  if (userId) {
    formData.append('user_id', userId);
  }

  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();

    // Track upload progress
    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable && onProgress) {
        const progress = Math.round((e.loaded / e.total) * 100);
        onProgress(progress);
      }
    });

    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const data = JSON.parse(xhr.responseText);
          resolve(data);
        } catch (error) {
          reject(new Error('Failed to parse server response'));
        }
      } else {
        try {
          const error = JSON.parse(xhr.responseText);
          reject(new Error(error.detail || `Upload failed with status ${xhr.status}`));
        } catch {
          reject(new Error(`Upload failed with status ${xhr.status}`));
        }
      }
    });

    xhr.addEventListener('error', () => {
      reject(new Error('Network error during upload'));
    });

    xhr.addEventListener('abort', () => {
      reject(new Error('Upload cancelled'));
    });

    xhr.open('POST', `${API_URL}/api/media/audio`);
    xhr.send(formData);
  });
};

export const getUserMedia = async (userId: string): Promise<UserMedia> => {
  const response = await fetch(`${API_URL}/api/media/user/${userId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch user media: ${response.status}`);
  }

  return response.json();
};

export const deletePhoto = async (userId: string, photoId: string): Promise<void> => {
  const response = await fetch(`${API_URL}/api/media/photo/${photoId}`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ user_id: userId }),
  });

  if (!response.ok) {
    throw new Error(`Failed to delete photo: ${response.status}`);
  }
};

export const deleteAudio = async (userId: string, audioId: string): Promise<void> => {
  const response = await fetch(`${API_URL}/api/media/audio/${audioId}`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ user_id: userId }),
  });

  if (!response.ok) {
    throw new Error(`Failed to delete audio: ${response.status}`);
  }
};

// Validation utilities
export const validatePhotoFile = (file: File): string | null => {
  const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
  const maxSize = 10 * 1024 * 1024; // 10MB

  if (!validTypes.includes(file.type)) {
    return 'Please upload a JPEG, PNG, or WebP image';
  }

  if (file.size > maxSize) {
    return 'Photo must be less than 10MB';
  }

  return null;
};

export const validateAudioFile = (file: File): string | null => {
  const validTypes = ['audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/webm', 'audio/ogg'];
  const maxSize = 5 * 1024 * 1024; // 5MB

  if (!validTypes.includes(file.type)) {
    return 'Please upload an MP3, WAV, WebM, or OGG audio file';
  }

  if (file.size > maxSize) {
    return 'Audio file must be less than 5MB';
  }

  return null;
};

export const validateAudioDuration = async (file: File): Promise<string | null> => {
  return new Promise((resolve) => {
    const audio = new Audio();
    const url = URL.createObjectURL(file);

    audio.addEventListener('loadedmetadata', () => {
      URL.revokeObjectURL(url);
      const duration = audio.duration;

      if (duration < 2 || duration > 5) {
        resolve('Audio must be between 2 and 5 seconds long');
      } else {
        resolve(null);
      }
    });

    audio.addEventListener('error', () => {
      URL.revokeObjectURL(url);
      resolve('Could not read audio file');
    });

    audio.src = url;
  });
};

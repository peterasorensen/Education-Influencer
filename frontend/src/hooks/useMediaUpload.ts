// Custom hook for managing media uploads

import { useState, useCallback } from 'react';
import { uploadPhoto, uploadAudio, deletePhoto, deleteAudio } from '../services/mediaApi';
import type { PhotoMetadata, AudioMetadata } from '../types/media';

interface UploadState {
  isUploading: boolean;
  progress: number;
  error: string | null;
}

export const useMediaUpload = () => {
  const [photoState, setPhotoState] = useState<UploadState>({
    isUploading: false,
    progress: 0,
    error: null,
  });

  const [audioState, setAudioState] = useState<UploadState>({
    isUploading: false,
    progress: 0,
    error: null,
  });

  const [uploadedPhoto, setUploadedPhoto] = useState<PhotoMetadata | null>(null);
  const [uploadedAudio, setUploadedAudio] = useState<AudioMetadata | null>(null);

  const handleUploadPhoto = useCallback(async (file: File, userId?: string) => {
    setPhotoState({ isUploading: true, progress: 0, error: null });

    try {
      const metadata = await uploadPhoto(file, userId, (progress) => {
        setPhotoState((prev) => ({ ...prev, progress }));
      });

      setUploadedPhoto(metadata);
      setPhotoState({ isUploading: false, progress: 100, error: null });
      return metadata;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to upload photo';
      setPhotoState({ isUploading: false, progress: 0, error: errorMessage });
      throw error;
    }
  }, []);

  const handleUploadAudio = useCallback(async (file: File, userId?: string) => {
    setAudioState({ isUploading: true, progress: 0, error: null });

    try {
      const metadata = await uploadAudio(file, userId, (progress) => {
        setAudioState((prev) => ({ ...prev, progress }));
      });

      setUploadedAudio(metadata);
      setAudioState({ isUploading: false, progress: 100, error: null });
      return metadata;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to upload audio';
      setAudioState({ isUploading: false, progress: 0, error: errorMessage });
      throw error;
    }
  }, []);

  const handleDeletePhoto = useCallback(async (userId: string, photoId: string) => {
    try {
      await deletePhoto(userId, photoId);
      setUploadedPhoto(null);
      setPhotoState({ isUploading: false, progress: 0, error: null });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to delete photo';
      setPhotoState((prev) => ({ ...prev, error: errorMessage }));
      throw error;
    }
  }, []);

  const handleDeleteAudio = useCallback(async (userId: string, audioId: string) => {
    try {
      await deleteAudio(userId, audioId);
      setUploadedAudio(null);
      setAudioState({ isUploading: false, progress: 0, error: null });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to delete audio';
      setAudioState((prev) => ({ ...prev, error: errorMessage }));
      throw error;
    }
  }, []);

  const clearPhoto = useCallback(() => {
    setUploadedPhoto(null);
    setPhotoState({ isUploading: false, progress: 0, error: null });
  }, []);

  const clearAudio = useCallback(() => {
    setUploadedAudio(null);
    setAudioState({ isUploading: false, progress: 0, error: null });
  }, []);

  const resetAll = useCallback(() => {
    clearPhoto();
    clearAudio();
  }, [clearPhoto, clearAudio]);

  return {
    // Photo state
    photoState,
    uploadedPhoto,
    uploadPhoto: handleUploadPhoto,
    deletePhoto: handleDeletePhoto,
    clearPhoto,

    // Audio state
    audioState,
    uploadedAudio,
    uploadAudio: handleUploadAudio,
    deleteAudio: handleDeleteAudio,
    clearAudio,

    // Global
    resetAll,
  };
};

// Media Types for Custom Celebrity Upload

export interface PhotoMetadata {
  photo_id: string;
  photo_url: string;
  thumbnail_url: string;
  filename: string;
  size_bytes: number;
  dimensions: {
    width: number;
    height: number;
  };
  created_at: string;
}

export interface AudioMetadata {
  audio_id: string;
  audio_url: string;
  filename: string;
  size_bytes: number;
  duration_seconds: number;
  sample_rate?: number;
  created_at: string;
}

export interface UserMedia {
  photos: PhotoMetadata[];
  audio: AudioMetadata[];
}

export type CelebrityMode = 'preset' | 'custom';

// Legacy single celebrity type (kept for backwards compatibility)
export type CelebritySelection =
  | {
      mode: 'preset';
      celebrity: 'drake' | 'sydney_sweeney';
    }
  | {
      mode: 'custom';
      photoId: string;
      audioId?: string;
    };

// New multi-celebrity types
export interface CelebrityConfig {
  mode: 'preset' | 'custom';
  name?: string;  // For preset - dynamically loaded from backend
  photoId?: string;  // For custom
  audioId?: string;  // For custom
  userId?: string;
  nanoBananaPrompt?: string;  // NEW - Optional AI image customization prompt
}

export type CelebritiesSelection = CelebrityConfig[];

export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

export interface ValidationError {
  field: string;
  message: string;
}

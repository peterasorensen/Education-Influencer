// API Types for Educational Video Generation App

export type PipelineStep =
  | 'generating_script'
  | 'creating_audio'
  | 'extracting_timestamps'
  | 'planning_visuals'
  | 'generating_animations'
  | 'creating_celebrity_videos'
  | 'lip_syncing'
  | 'compositing_video';

export interface ProgressUpdate {
  step: PipelineStep;
  status: 'pending' | 'in_progress' | 'completed' | 'error';
  message?: string;
  progress?: number; // 0-100
}

export interface VideoGenerationRequest {
  topic: string;
  renderer?: 'manim' | 'remotion'; // Animation renderer (default: manim)
}

export interface VideoGenerationResponse {
  jobId: string;
  message: string;
  websocketUrl?: string;
}

export interface VideoGenerationComplete {
  videoUrl: string;
  duration: number;
  topic: string;
}

export interface ErrorResponse {
  error: string;
  details?: string;
}

export type ConnectionState = 'disconnected' | 'connecting' | 'connected' | 'error';

export interface StepInfo {
  key: PipelineStep;
  label: string;
  description: string;
}

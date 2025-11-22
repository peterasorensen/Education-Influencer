// Custom hook for recording audio with MediaRecorder API

import { useState, useRef, useCallback, useEffect } from 'react';

interface RecorderState {
  isRecording: boolean;
  isPaused: boolean;
  recordingTime: number;
  audioBlob: Blob | null;
  audioUrl: string | null;
  error: string | null;
  permissionGranted: boolean;
}

interface WaveformData {
  dataArray: Uint8Array;
  bufferLength: number;
}

const MAX_RECORDING_TIME = 5; // seconds

export const useAudioRecorder = () => {
  const [state, setState] = useState<RecorderState>({
    isRecording: false,
    isPaused: false,
    recordingTime: 0,
    audioBlob: null,
    audioUrl: null,
    error: null,
    permissionGranted: false,
  });

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const analyzerRef = useRef<AnalyserNode | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const waveformCallbackRef = useRef<((data: WaveformData) => void) | null>(null);
  const animationFrameRef = useRef<number | null>(null);

  // Request microphone permission
  const requestPermission = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      setState((prev) => ({ ...prev, permissionGranted: true, error: null }));
      return true;
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Microphone access denied';
      setState((prev) => ({
        ...prev,
        permissionGranted: false,
        error: errorMessage,
      }));
      return false;
    }
  }, []);

  // Start recording
  const startRecording = useCallback(async () => {
    // Request permission if not already granted
    if (!streamRef.current) {
      const granted = await requestPermission();
      if (!granted) return;
    }

    try {
      audioChunksRef.current = [];

      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(streamRef.current!, {
        mimeType: 'audio/webm',
      });

      mediaRecorderRef.current = mediaRecorder;

      // Setup audio analyzer for waveform
      audioContextRef.current = new AudioContext();
      const source = audioContextRef.current.createMediaStreamSource(streamRef.current!);
      analyzerRef.current = audioContextRef.current.createAnalyser();
      analyzerRef.current.fftSize = 2048;
      source.connect(analyzerRef.current);

      // Collect audio data
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      // Handle recording stop
      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const audioUrl = URL.createObjectURL(audioBlob);

        setState((prev) => ({
          ...prev,
          audioBlob,
          audioUrl,
          isRecording: false,
        }));

        // Cleanup
        if (timerRef.current) {
          clearInterval(timerRef.current);
          timerRef.current = null;
        }
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current);
          animationFrameRef.current = null;
        }
      };

      // Start recording
      mediaRecorder.start(100); // Collect data every 100ms

      // Start timer
      let elapsed = 0;
      setState((prev) => ({ ...prev, isRecording: true, recordingTime: 0 }));

      timerRef.current = setInterval(() => {
        elapsed += 0.1;
        setState((prev) => ({ ...prev, recordingTime: elapsed }));

        // Auto-stop at max time
        if (elapsed >= MAX_RECORDING_TIME) {
          stopRecording();
        }
      }, 100);

      // Start waveform animation
      updateWaveform();
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to start recording';
      setState((prev) => ({ ...prev, error: errorMessage }));
    }
  }, [requestPermission]);

  // Update waveform data
  const updateWaveform = useCallback(() => {
    if (!analyzerRef.current || !waveformCallbackRef.current) {
      animationFrameRef.current = requestAnimationFrame(updateWaveform);
      return;
    }

    const bufferLength = analyzerRef.current.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    analyzerRef.current.getByteTimeDomainData(dataArray);

    waveformCallbackRef.current({ dataArray, bufferLength });
    animationFrameRef.current = requestAnimationFrame(updateWaveform);
  }, []);

  // Stop recording
  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
  }, []);

  // Clear recording
  const clearRecording = useCallback(() => {
    if (state.audioUrl) {
      URL.revokeObjectURL(state.audioUrl);
    }
    setState((prev) => ({
      ...prev,
      audioBlob: null,
      audioUrl: null,
      recordingTime: 0,
    }));
  }, [state.audioUrl]);

  // Set waveform callback
  const setWaveformCallback = useCallback((callback: (data: WaveformData) => void) => {
    waveformCallbackRef.current = callback;
  }, []);

  // Convert blob to File
  const getAudioFile = useCallback((): File | null => {
    if (!state.audioBlob) return null;
    return new File([state.audioBlob], `recording-${Date.now()}.webm`, {
      type: 'audio/webm',
    });
  }, [state.audioBlob]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (state.audioUrl) {
        URL.revokeObjectURL(state.audioUrl);
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, [state.audioUrl]);

  return {
    ...state,
    maxRecordingTime: MAX_RECORDING_TIME,
    requestPermission,
    startRecording,
    stopRecording,
    clearRecording,
    setWaveformCallback,
    getAudioFile,
  };
};

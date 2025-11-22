import { useCallback } from 'react';
import { useRecordingStore } from '../store';

export const useRecording = () => {
  const {
    isRecording,
    selectedArea,
    selectedSourceId,
    micEnabled,
    mediaStream,
    mediaRecorder,
    setMediaStream,
    setMediaRecorder,
    setIsRecording,
    addRecordedChunk,
    clearRecordedChunks,
  } = useRecordingStore();

  const startRecording = useCallback(async () => {
    try {
      console.log('useRecording: startRecording called');
      console.log('useRecording: selectedSourceId =', selectedSourceId);
      console.log('useRecording: selectedArea =', selectedArea);

      clearRecordedChunks();

      let videoStream: MediaStream | null = null;

      if (selectedSourceId) {
        console.log('useRecording: Using selectedSourceId path');
        // Window or Display recording
        const constraints = {
          audio: false,
          video: {
            mandatory: {
              chromeMediaSource: 'desktop',
              chromeMediaSourceId: selectedSourceId,
            },
          } as any,
        };

        videoStream = await navigator.mediaDevices.getUserMedia(constraints);
      } else if (selectedArea) {
        console.log('useRecording: Using selectedArea path');
        // Area recording - we'll use screen capture and crop in post
        // For now, capture the entire screen (cropping would be done during export)
        const sources = await window.electronAPI.getSources();
        const screenSource = sources.find((s) => s.id.startsWith('screen'));
        console.log('useRecording: Found screen source:', screenSource?.id);

        if (screenSource) {
          const constraints = {
            audio: false,
            video: {
              mandatory: {
                chromeMediaSource: 'desktop',
                chromeMediaSourceId: screenSource.id,
              },
            } as any,
          };

          videoStream = await navigator.mediaDevices.getUserMedia(constraints);
        }
      }

      if (!videoStream) {
        console.error('useRecording: No video stream - selectedSourceId:', selectedSourceId, 'selectedArea:', selectedArea);
        throw new Error('Failed to get video stream');
      }

      console.log('useRecording: Got video stream successfully');

      // Add audio if microphone is enabled
      let audioStream: MediaStream | null = null;
      if (micEnabled) {
        try {
          audioStream = await navigator.mediaDevices.getUserMedia({
            audio: {
              echoCancellation: true,
              noiseSuppression: true,
              sampleRate: 44100,
            },
            video: false,
          });
        } catch (error) {
          console.error('Failed to get audio stream:', error);
          // Continue without audio if mic fails
        }
      }

      // Combine video and audio streams
      let combinedStream: MediaStream;

      if (audioStream) {
        const videoTrack = videoStream.getVideoTracks()[0];
        const audioTrack = audioStream.getAudioTracks()[0];
        combinedStream = new MediaStream([videoTrack, audioTrack]);
      } else {
        combinedStream = videoStream;
      }

      setMediaStream(combinedStream);

      // Create MediaRecorder
      const options = {
        mimeType: 'video/webm;codecs=vp9',
        videoBitsPerSecond: 8000000, // 8 Mbps
      };

      // Fallback to vp8 if vp9 is not supported
      let recorder: MediaRecorder;
      try {
        recorder = new MediaRecorder(combinedStream, options);
      } catch (e) {
        const fallbackOptions = {
          mimeType: 'video/webm;codecs=vp8',
          videoBitsPerSecond: 5000000, // 5 Mbps
        };
        recorder = new MediaRecorder(combinedStream, fallbackOptions);
      }

      recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          addRecordedChunk(event.data);
        }
      };

      recorder.onstart = () => {
        console.log('Recording started');
        setIsRecording(true);
      };

      recorder.onstop = () => {
        console.log('Recording stopped');
        setIsRecording(false);

        // Stop all tracks
        if (combinedStream) {
          combinedStream.getTracks().forEach((track) => track.stop());
        }
      };

      recorder.onerror = (event: Event) => {
        console.error('MediaRecorder error:', event);
      };

      setMediaRecorder(recorder);

      // Start recording with 1-second chunks
      recorder.start(1000);
    } catch (error) {
      console.error('Error starting recording:', error);
      alert(`Failed to start recording: ${error}`);
    }
  }, [
    selectedSourceId,
    selectedArea,
    micEnabled,
    setMediaStream,
    setMediaRecorder,
    setIsRecording,
    addRecordedChunk,
    clearRecordedChunks,
  ]);

  const stopRecording = useCallback(() => {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
    }

    if (mediaStream) {
      mediaStream.getTracks().forEach((track) => track.stop());
      setMediaStream(null);
    }

    setMediaRecorder(null);
  }, [mediaRecorder, mediaStream, setMediaStream, setMediaRecorder]);

  return {
    startRecording,
    stopRecording,
    isRecording,
  };
};

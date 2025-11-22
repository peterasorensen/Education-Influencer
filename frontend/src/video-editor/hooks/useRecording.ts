import { useCallback } from 'react';
import { useRecordingStore } from '../store';

export const useRecording = () => {
  const {
    isRecording,
    selectedArea,
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
      console.log('useRecording: selectedArea =', selectedArea);

      clearRecordedChunks();

      // Use getDisplayMedia for screen capture
      const displayMediaOptions: DisplayMediaStreamOptions = {
        video: {
          displaySurface: 'monitor',
        } as MediaTrackConstraints,
        audio: false,
      };

      const videoStream = await navigator.mediaDevices.getDisplayMedia(displayMediaOptions);
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
      mediaStream.getTracks().forEach((track: MediaStreamTrack) => track.stop());
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

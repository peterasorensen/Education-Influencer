import React, { useEffect, useState, useRef } from 'react';
import styled from 'styled-components';
import { useRecordingStore } from '../store';
import { useRecording } from '../hooks/useRecording';
import { PlayIcon, PauseIcon, RestartIcon, StopIcon, TrashIcon } from './Icons';

const Container = styled.div`
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  -webkit-app-region: drag;
`;

const ToolbarContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  background: ${({ theme }) => theme.colors.background.glass};
  backdrop-filter: blur(20px);
  border: 1px solid ${({ theme }) => theme.colors.border.primary};
  border-radius: ${({ theme }) => theme.borderRadius.full};
  animation: fadeIn 0.3s ease-out;
  -webkit-app-region: drag;
`;

const RecordingIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  -webkit-app-region: drag;
`;

const RecDot = styled.div`
  width: 10px;
  height: 10px;
  background: ${({ theme }) => theme.colors.status.recording};
  border-radius: 50%;
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  box-shadow: 0 0 10px ${({ theme }) => theme.colors.status.recording};
  -webkit-app-region: drag;
`;

const Timer = styled.span`
  font-size: 14px;
  font-weight: 600;
  color: ${({ theme }) => theme.colors.text.primary};
  font-variant-numeric: tabular-nums;
  min-width: 60px;
  -webkit-app-region: drag;
`;

const Divider = styled.div`
  width: 1px;
  height: 28px;
  background: ${({ theme }) => theme.colors.border.primary};
  -webkit-app-region: drag;
`;

const ToolbarButton = styled.button<{ $variant?: 'danger' }>`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 14px;
  background: ${({ $variant, theme }) =>
    $variant === 'danger' ? theme.colors.status.recording : 'transparent'};
  color: ${({ theme }) => theme.colors.text.primary};
  border-radius: ${({ theme }) => theme.borderRadius.md};
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all ${({ theme }) => theme.transitions.fast};
  white-space: nowrap;
  -webkit-app-region: no-drag;

  &:hover {
    background: ${({ $variant, theme }) =>
      $variant === 'danger'
        ? '#dc2626'
        : theme.colors.background.tertiary};
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const IconButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: transparent;
  color: ${({ theme }) => theme.colors.text.primary};
  border-radius: ${({ theme }) => theme.borderRadius.md};
  cursor: pointer;
  transition: all ${({ theme }) => theme.transitions.fast};
  font-size: 18px;
  -webkit-app-region: no-drag;

  &:hover {
    background: ${({ theme }) => theme.colors.background.tertiary};
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const RecordingToolbar: React.FC = () => {
  const {
    isPaused,
    recordingTime,
    setIsPaused,
    setRecordingTime,
    mediaRecorder,
    reset,
    setSelectedSourceId,
    setSelectedArea,
  } = useRecordingStore();

  const { startRecording, stopRecording } = useRecording();
  const [startTime, setStartTime] = useState(Date.now());
  const hasInitialized = useRef(false);
  const [configLoaded, setConfigLoaded] = useState(false);

  // First effect: Load config on mount
  useEffect(() => {
    if (hasInitialized.current) {
      console.log('RecordingToolbar: Already initialized, skipping');
      return;
    }
    hasInitialized.current = true;
    console.log('RecordingToolbar: Initializing...');

    // Fetch recording config
    const initRecording = async () => {
      const config = await window.electronAPI.getRecordingConfig();
      console.log('RecordingToolbar: Received config from main process:', config);

      if (config) {
        if (config.selectedSourceId) {
          console.log('RecordingToolbar: Setting selectedSourceId:', config.selectedSourceId);
          setSelectedSourceId(config.selectedSourceId);
        }
        if (config.selectedArea) {
          console.log('RecordingToolbar: Setting selectedArea:', config.selectedArea);
          setSelectedArea(config.selectedArea);
        }
        setConfigLoaded(true);
      }
    };

    initRecording();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Second effect: Start recording once config is loaded and startRecording is ready
  useEffect(() => {
    if (configLoaded) {
      console.log('RecordingToolbar: Config loaded, starting recording...');
      startRecording();
      setConfigLoaded(false); // Only start once
    }
  }, [configLoaded, startRecording]);

  useEffect(() => {
    // Start the timer
    const interval = setInterval(() => {
      if (!isPaused) {
        setRecordingTime(Math.floor((Date.now() - startTime) / 1000));
      }
    }, 100);

    return () => clearInterval(interval);
  }, [isPaused, startTime, setRecordingTime]);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handlePauseResume = () => {
    if (mediaRecorder) {
      if (isPaused) {
        mediaRecorder.resume();
        setStartTime(Date.now() - recordingTime * 1000);
      } else {
        mediaRecorder.pause();
      }
      setIsPaused(!isPaused);
    }
  };

  const handleRestart = async () => {
    stopRecording();
    reset();
    setRecordingTime(0);
    setIsPaused(false);
    setStartTime(Date.now());
    // Restart recording after a brief delay
    setTimeout(() => {
      startRecording();
    }, 100);
  };

  const handleCancel = () => {
    // Stop recording without saving
    stopRecording();
    reset();
    // Go back to control bar
    window.electronAPI.stopRecording();
  };

  const handleFinish = async () => {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      // Set up the stop handler before stopping
      const stopHandler = async () => {
        // Give it a moment for final chunks to arrive
        await new Promise(resolve => setTimeout(resolve, 200));

        // Get the current chunks from the store at the time of stopping
        const currentChunks = useRecordingStore.getState().recordedChunks;

        console.log('Recorded chunks count:', currentChunks.length);
        console.log('Total size:', currentChunks.reduce((acc, chunk) => acc + chunk.size, 0), 'bytes');

        if (currentChunks.length === 0) {
          console.error('No recorded chunks available!');
          alert('Recording failed: No data captured');
          reset();
          return;
        }

        const blob = new Blob(currentChunks, { type: 'video/webm' });
        console.log('Blob size:', blob.size, 'bytes');

        const arrayBuffer = await blob.arrayBuffer();
        const uint8Array = new Uint8Array(arrayBuffer);

        // Open editor with the recording data
        window.electronAPI.openEditor(uint8Array);

        // Reset state
        reset();
      };

      mediaRecorder.onstop = stopHandler;
      mediaRecorder.stop();
    } else {
      // If not recording, just close
      window.electronAPI.stopRecording();
    }
  };

  return (
    <Container>
      <ToolbarContainer>
        <IconButton onClick={handleCancel} title="Cancel recording">
          <TrashIcon size={18} />
        </IconButton>

        <Divider />

        <RecordingIndicator>
          <RecDot />
          <Timer>{formatTime(recordingTime)}</Timer>
        </RecordingIndicator>

        <Divider />

        <IconButton
          onClick={handlePauseResume}
          title={isPaused ? 'Resume' : 'Pause'}
        >
          {isPaused ? <PlayIcon size={18} /> : <PauseIcon size={18} />}
        </IconButton>

        <IconButton onClick={handleRestart} title="Restart">
          <RestartIcon size={18} />
        </IconButton>

        <Divider />

        <ToolbarButton $variant="danger" onClick={handleFinish}>
          <StopIcon size={16} />
          <span>Finish</span>
        </ToolbarButton>
      </ToolbarContainer>
    </Container>
  );
};

export default RecordingToolbar;

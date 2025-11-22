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

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
`;

const RecordingIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const RecDot = styled.div`
  width: 10px;
  height: 10px;
  background: ${({ theme }) => theme.colors.status.recording};
  border-radius: 50%;
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  box-shadow: 0 0 10px ${({ theme }) => theme.colors.status.recording};

  @keyframes pulse {
    0%, 100% {
      opacity: 1;
    }
    50% {
      opacity: 0.5;
    }
  }
`;

const Timer = styled.span`
  font-size: 14px;
  font-weight: 600;
  color: ${({ theme }) => theme.colors.text.primary};
  font-variant-numeric: tabular-nums;
  min-width: 60px;
`;

const Divider = styled.div`
  width: 1px;
  height: 28px;
  background: ${({ theme }) => theme.colors.border.primary};
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
  border: none;
  border-radius: ${({ theme }) => theme.borderRadius.md};
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all ${({ theme }) => theme.transitions.fast};
  white-space: nowrap;

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
  border: none;
  color: ${({ theme }) => theme.colors.text.primary};
  border-radius: ${({ theme }) => theme.borderRadius.md};
  cursor: pointer;
  transition: all ${({ theme }) => theme.transitions.fast};
  font-size: 18px;

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

interface RecordingToolbarProps {
  onFinish?: (blob: Blob) => void;
  onCancel?: () => void;
  autoStart?: boolean;
}

const RecordingToolbar: React.FC<RecordingToolbarProps> = ({ onFinish, onCancel, autoStart = false }) => {
  const {
    isPaused,
    recordingTime,
    setIsPaused,
    setRecordingTime,
    mediaRecorder,
    reset,
  } = useRecordingStore();

  const { startRecording, stopRecording } = useRecording();
  const [startTime, setStartTime] = useState(Date.now());
  const hasInitialized = useRef(false);

  // Auto-start recording if enabled
  useEffect(() => {
    if (autoStart && !hasInitialized.current) {
      hasInitialized.current = true;
      console.log('RecordingToolbar: Auto-starting recording...');
      startRecording();
    }
  }, [autoStart, startRecording]);

  // Update timer
  useEffect(() => {
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
    stopRecording();
    reset();
    if (onCancel) {
      onCancel();
    }
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
        console.log('Total size:', currentChunks.reduce((acc: number, chunk: Blob) => acc + chunk.size, 0), 'bytes');

        if (currentChunks.length === 0) {
          console.error('No recorded chunks available!');
          alert('Recording failed: No data captured');
          reset();
          return;
        }

        const blob = new Blob(currentChunks, { type: 'video/webm' });
        console.log('Blob size:', blob.size, 'bytes');

        if (onFinish) {
          onFinish(blob);
        }

        // Reset state
        reset();
      };

      mediaRecorder.onstop = stopHandler;
      mediaRecorder.stop();
    } else {
      // If not recording, just close
      if (onCancel) {
        onCancel();
      }
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

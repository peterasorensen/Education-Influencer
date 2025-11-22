import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useRecordingStore } from '../store';
import { CloseIcon } from './Icons';

const FullscreenOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.3);
  cursor: crosshair;
  z-index: ${({ theme }) => theme.zIndex.overlay};
`;

const SelectionBox = styled.div<{ $x: number; $y: number; $width: number; $height: number }>`
  position: absolute;
  left: ${({ $x }) => $x}px;
  top: ${({ $y }) => $y}px;
  width: ${({ $width }) => $width}px;
  height: ${({ $height }) => $height}px;
  border: 3px solid ${({ theme }) => theme.colors.accent.primary};
  background: rgba(124, 58, 237, 0.1);
  box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.4), ${({ theme }) => theme.shadows.glowLg};
  border-radius: ${({ theme }) => theme.borderRadius.sm};
  pointer-events: none;
  backdrop-filter: blur(0px);
`;

const DimensionLabel = styled.div`
  position: absolute;
  top: -32px;
  left: 0;
  background: ${({ theme }) => theme.colors.background.glass};
  backdrop-filter: blur(20px);
  color: ${({ theme }) => theme.colors.text.primary};
  padding: 4px 12px;
  border-radius: ${({ theme }) => theme.borderRadius.md};
  font-size: 12px;
  font-weight: 600;
  border: 1px solid ${({ theme }) => theme.colors.border.accent};
  box-shadow: ${({ theme }) => theme.shadows.md};
  white-space: nowrap;
`;

const StartButton = styled.button<{ $x: number; $y: number; $width: number; $height: number }>`
  position: absolute;
  left: ${({ $x, $width }) => $x + $width / 2}px;
  top: ${({ $y, $height }) => $y + $height + 20}px;
  transform: translateX(-50%);
  padding: 12px 32px;
  background: ${({ theme }) => theme.colors.accent.primary};
  color: ${({ theme }) => theme.colors.text.primary};
  border: 1px solid ${({ theme }) => theme.colors.accent.hover};
  border-radius: ${({ theme }) => theme.borderRadius.full};
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all ${({ theme }) => theme.transitions.fast};
  box-shadow: ${({ theme }) => theme.shadows.glow};
  animation: fadeIn 0.2s ease-out;

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateX(-50%) translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateX(-50%) translateY(0);
    }
  }

  &:hover {
    background: ${({ theme }) => theme.colors.accent.hover};
    transform: translateX(-50%) translateY(-2px);
    box-shadow: ${({ theme }) => theme.shadows.glowLg};
  }

  &:active {
    transform: translateX(-50%) translateY(0);
  }
`;

const CloseButton = styled.button`
  position: absolute;
  top: 20px;
  right: 20px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: ${({ theme }) => theme.colors.background.glass};
  backdrop-filter: blur(20px);
  border: 1px solid ${({ theme }) => theme.colors.border.primary};
  border-radius: ${({ theme }) => theme.borderRadius.full};
  color: ${({ theme }) => theme.colors.text.primary};
  cursor: pointer;
  transition: all ${({ theme }) => theme.transitions.fast};
  font-size: 20px;

  &:hover {
    background: ${({ theme }) => theme.colors.status.recording};
    border-color: ${({ theme }) => theme.colors.status.recording};
    transform: scale(1.1);
  }
`;

interface SelectionWindowProps {
  mode: 'area' | 'window' | 'display';
  onClose?: () => void;
  onStartRecording?: () => void;
}

const SelectionWindow: React.FC<SelectionWindowProps> = ({ mode, onClose, onStartRecording }) => {
  const [isDrawing, setIsDrawing] = useState(false);
  const [startPos, setStartPos] = useState({ x: 0, y: 0 });
  const [currentPos, setCurrentPos] = useState({ x: 0, y: 0 });
  const { setSelectedArea, setRecordingMode } = useRecordingStore();

  useEffect(() => {
    setRecordingMode(mode);

    // ESC key to close
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        if (onClose) {
          onClose();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [mode, onClose, setRecordingMode]);

  const handleMouseDown = (e: React.MouseEvent) => {
    if (mode !== 'area') return;
    setIsDrawing(true);
    setStartPos({ x: e.clientX, y: e.clientY });
    setCurrentPos({ x: e.clientX, y: e.clientY });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDrawing || mode !== 'area') return;
    setCurrentPos({ x: e.clientX, y: e.clientY });
  };

  const handleMouseUp = () => {
    if (mode !== 'area') return;
    setIsDrawing(false);
  };

  const getSelectionBox = () => {
    const x = Math.min(startPos.x, currentPos.x);
    const y = Math.min(startPos.y, currentPos.y);
    const width = Math.abs(currentPos.x - startPos.x);
    const height = Math.abs(currentPos.y - startPos.y);
    return { x, y, width, height };
  };

  const handleStartRecording = async () => {
    const box = getSelectionBox();
    setSelectedArea(box);

    console.log('SelectionWindow (Area): Selected area:', box);

    if (onStartRecording) {
      onStartRecording();
    }
  };

  const handleClose = () => {
    if (onClose) {
      onClose();
    }
  };

  const box = getSelectionBox();

  // For area mode, allow user to draw a selection
  if (mode === 'area') {
    return (
      <FullscreenOverlay
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
      >
        <CloseButton onClick={handleClose}>
          <CloseIcon size={20} />
        </CloseButton>
        {box.width > 10 && box.height > 10 && (
          <>
            <SelectionBox $x={box.x} $y={box.y} $width={box.width} $height={box.height}>
              <DimensionLabel>
                {Math.round(box.width)} × {Math.round(box.height)}
              </DimensionLabel>
            </SelectionBox>
            <StartButton
              $x={box.x}
              $y={box.y}
              $width={box.width}
              $height={box.height}
              onClick={handleStartRecording}
            >
              Start Recording
            </StartButton>
          </>
        )}
      </FullscreenOverlay>
    );
  }

  // For window/display mode, the browser's native picker is used via getDisplayMedia
  // So this component just triggers the recording immediately
  useEffect(() => {
    if (mode === 'window' || mode === 'display') {
      // Automatically start recording which will trigger the browser's picker
      if (onStartRecording) {
        onStartRecording();
      }
      // Close the selection window after triggering
      if (onClose) {
        setTimeout(() => onClose(), 100);
      }
    }
  }, [mode, onStartRecording, onClose]);

  return null;
};

export default SelectionWindow;

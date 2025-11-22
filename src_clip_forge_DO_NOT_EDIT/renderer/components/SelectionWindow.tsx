import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useRecordingStore } from '../store';
import { CloseIcon } from './Icons';
import DisplaySelectionOverlay from './DisplaySelectionOverlay';
import WindowSelectionOverlay from './WindowSelectionOverlay';
import type { Display } from '../../main/preload';

const FullscreenOverlay = styled.div`
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.3);
  position: relative;
  cursor: crosshair;
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
  border-radius: ${({ theme }) => theme.borderRadius.full};
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all ${({ theme }) => theme.transitions.fast};
  box-shadow: ${({ theme }) => theme.shadows.glow};
  border: 1px solid ${({ theme }) => theme.colors.accent.hover};
  animation: fadeIn 0.2s ease-out;

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
}

interface Source {
  id: string;
  name: string;
  thumbnail: string;
  appIcon?: string;
  bounds?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}

type DisplayInfo = Display;

const SelectionWindow: React.FC<SelectionWindowProps> = ({ mode }) => {
  const [isDrawing, setIsDrawing] = useState(false);
  const [startPos, setStartPos] = useState({ x: 0, y: 0 });
  const [currentPos, setCurrentPos] = useState({ x: 0, y: 0 });
  const [sources, setSources] = useState<Source[]>([]);
  const [displays, setDisplays] = useState<DisplayInfo[]>([]);
  const { setSelectedArea, setSelectedSourceId } = useRecordingStore();

  useEffect(() => {
    if (mode === 'window') {
      loadSources();
    } else if (mode === 'display') {
      loadDisplays();
    }

    // ESC key to close
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        window.electronAPI.closeSelection();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [mode]);

  const loadDisplays = async () => {
    try {
      const displayList = await window.electronAPI.getDisplays();
      setDisplays(displayList);
    } catch (error) {
      console.error('Error loading displays:', error);
    }
  };

  const loadSources = async () => {
    try {
      const allSources = await window.electronAPI.getSources();
      // Filter for windows only
      const windows = allSources.filter((source) => !source.id.startsWith('screen'));
      setSources(windows);
    } catch (error) {
      console.error('Error loading sources:', error);
    }
  };

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
    // For area mode, we still need to get a screen source
    const allSources = await window.electronAPI.getSources();
    const screenSource = allSources.find((s) => s.id.startsWith('screen'));
    let sourceId: string | null = null;
    if (screenSource) {
      sourceId = screenSource.id;
      setSelectedSourceId(screenSource.id);
    }

    console.log('SelectionWindow (Area): Sending config to main process:', {
      selectedSourceId: sourceId,
      selectedArea: box,
    });

    // Notify main process and trigger recording toolbar with config
    window.electronAPI.startRecording({
      selectedSourceId: sourceId,
      selectedArea: box,
    });
  };

  const handleDisplaySelect = async (display: DisplayInfo) => {
    // Get the screen source for this display
    const allSources = await window.electronAPI.getSources();
    const screenSource = allSources.find((s) => s.id.startsWith('screen') && s.id.includes(String(display.id)));

    // If we can't match by ID, just use the first screen source (for single display setups)
    const sourceToUse = screenSource || allSources.find((s) => s.id.startsWith('screen'));

    let sourceId: string | null = null;
    if (sourceToUse) {
      sourceId = sourceToUse.id;
      setSelectedSourceId(sourceToUse.id);
    }

    console.log('SelectionWindow (Display): Sending config to main process:', {
      selectedSourceId: sourceId,
      selectedArea: null,
    });

    // Notify main process and trigger recording toolbar with config
    window.electronAPI.startRecording({
      selectedSourceId: sourceId,
      selectedArea: null,
    });
  };

  const handleWindowSelect = async (selectedWindow: Source) => {
    setSelectedSourceId(selectedWindow.id);

    console.log('SelectionWindow (Window): Sending config to main process:', {
      selectedSourceId: selectedWindow.id,
      selectedArea: null,
    });

    // Notify main process and trigger recording toolbar with config
    window.electronAPI.startRecording({
      selectedSourceId: selectedWindow.id,
      selectedArea: null,
    });
  };

  const handleClose = () => {
    window.electronAPI.closeSelection();
  };

  const box = getSelectionBox();

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

  // Display mode uses a different overlay
  if (mode === 'display') {
    return (
      <DisplaySelectionOverlay
        displays={displays}
        onSelect={handleDisplaySelect}
        onClose={handleClose}
      />
    );
  }

  // Window mode - hover-based selection
  if (mode === 'window') {
    return (
      <WindowSelectionOverlay
        windows={sources}
        onSelect={handleWindowSelect}
        onClose={handleClose}
      />
    );
  }

  // Area mode
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
};

export default SelectionWindow;

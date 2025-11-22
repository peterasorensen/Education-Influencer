import React, { useState } from 'react';
import styled from 'styled-components';
import { CloseIcon } from './Icons';
import type { Display } from '../../main/preload';

const FullscreenContainer = styled.div`
  width: 100vw;
  height: 100vh;
  position: relative;
`;

const DisplayOverlay = styled.div<{ $bounds: { x: number; y: number; width: number; height: number }; $isHovered: boolean; $isSelected: boolean }>`
  position: absolute;
  left: ${({ $bounds }) => $bounds.x}px;
  top: ${({ $bounds }) => $bounds.y}px;
  width: ${({ $bounds }) => $bounds.width}px;
  height: ${({ $bounds }) => $bounds.height}px;
  border: none;
  border-radius: 12px;
  background: ${({ $isHovered, $isSelected }) =>
    $isHovered || $isSelected ? 'rgba(124, 58, 237, 0.15)' : 'transparent'};
  cursor: pointer;
  transition: all ${({ theme }) => theme.transitions.fast};
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: ${({ $isSelected, $isHovered }) =>
    $isSelected ? '0 0 0 3px rgba(124, 58, 237, 0.6), 0 8px 32px rgba(124, 58, 237, 0.4)' :
    $isHovered ? '0 0 0 2px rgba(124, 58, 237, 0.4)' : 'none'};
`;

const DisplayInfo = styled.div`
  background: ${({ theme }) => theme.colors.background.glass};
  backdrop-filter: blur(20px);
  padding: 24px 32px;
  border-radius: ${({ theme }) => theme.borderRadius.lg};
  border: 1px solid ${({ theme }) => theme.colors.border.accent};
  box-shadow: ${({ theme }) => theme.shadows.md};
  text-align: center;
  animation: fadeIn 0.2s ease-out;
  pointer-events: none;
`;

const DisplayName = styled.h2`
  font-size: 32px;
  font-weight: 700;
  color: ${({ theme }) => theme.colors.text.primary};
  margin-bottom: 8px;
`;

const DisplaySpecs = styled.p`
  font-size: 18px;
  font-weight: 500;
  color: ${({ theme }) => theme.colors.text.secondary};
`;

const StartButton = styled.button`
  position: fixed;
  bottom: 60px;
  left: 50%;
  transform: translateX(-50%);
  padding: 16px 48px;
  background: ${({ theme }) => theme.colors.accent.primary};
  color: ${({ theme }) => theme.colors.text.primary};
  border-radius: ${({ theme }) => theme.borderRadius.full};
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: all ${({ theme }) => theme.transitions.fast};
  box-shadow: ${({ theme }) => theme.shadows.glow};
  border: 1px solid ${({ theme }) => theme.colors.accent.hover};
  animation: fadeIn 0.3s ease-out;

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
  position: fixed;
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

type DisplayInfo = Display;

interface DisplaySelectionOverlayProps {
  displays: DisplayInfo[];
  onSelect: (display: DisplayInfo) => Promise<void>;
  onClose: () => void;
}

const DisplaySelectionOverlay: React.FC<DisplaySelectionOverlayProps> = ({
  displays,
  onSelect,
  onClose,
}) => {
  const [hoveredDisplay, setHoveredDisplay] = useState<DisplayInfo | null>(null);
  const [selectedDisplay, setSelectedDisplay] = useState<DisplayInfo | null>(null);

  const handleDisplayClick = (display: DisplayInfo) => {
    setSelectedDisplay(display);
  };

  const handleStartRecording = () => {
    if (selectedDisplay) {
      onSelect(selectedDisplay);
    }
  };

  const getDisplayName = (display: DisplayInfo) => {
    if (display.internal) {
      return 'Built-in Retina Display';
    }
    return `External Display ${display.id}`;
  };

  const getDisplaySpecs = (display: DisplayInfo) => {
    const { width, height } = display.size;
    const scaleFactor = display.scaleFactor;
    const fps = 60; // Default, could be enhanced to detect actual refresh rate
    return `${width}×${height} • ${fps * scaleFactor}FPS`;
  };

  return (
    <FullscreenContainer>
      <CloseButton onClick={onClose}>
        <CloseIcon size={20} />
      </CloseButton>

      {displays.map((display) => (
        <DisplayOverlay
          key={display.id}
          $bounds={display.bounds}
          $isHovered={hoveredDisplay?.id === display.id}
          $isSelected={selectedDisplay?.id === display.id}
          onMouseEnter={() => setHoveredDisplay(display)}
          onMouseLeave={() => setHoveredDisplay(null)}
          onClick={() => handleDisplayClick(display)}
        >
          {(hoveredDisplay?.id === display.id || selectedDisplay?.id === display.id) && (
            <DisplayInfo>
              <DisplayName>{getDisplayName(display)}</DisplayName>
              <DisplaySpecs>{getDisplaySpecs(display)}</DisplaySpecs>
            </DisplayInfo>
          )}
        </DisplayOverlay>
      ))}

      {selectedDisplay && (
        <StartButton onClick={handleStartRecording}>
          Start recording
        </StartButton>
      )}
    </FullscreenContainer>
  );
};

export default DisplaySelectionOverlay;

import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { CloseIcon } from './Icons';

const FullscreenContainer = styled.div`
  width: 100vw;
  height: 100vh;
  position: relative;
  background: rgba(0, 0, 0, 0.3);
`;

const WindowOverlay = styled.div<{
  $bounds: { x: number; y: number; width: number; height: number };
  $isHovered: boolean;
  $isSelected: boolean
}>`
  position: fixed;
  left: ${({ $bounds }) => $bounds.x}px;
  top: ${({ $bounds }) => $bounds.y}px;
  width: ${({ $bounds }) => $bounds.width}px;
  height: ${({ $bounds }) => $bounds.height}px;
  border: none;
  border-radius: 12px;
  background: ${({ $isHovered, $isSelected }) =>
    $isHovered || $isSelected ? 'rgba(124, 58, 237, 0.2)' : 'transparent'};
  cursor: pointer;
  transition: all ${({ theme }) => theme.transitions.fast};
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: ${({ $isSelected, $isHovered }) =>
    $isSelected ? '0 0 0 3px rgba(124, 58, 237, 0.6), 0 8px 32px rgba(124, 58, 237, 0.4)' :
    $isHovered ? '0 0 0 2px rgba(124, 58, 237, 0.4)' : 'none'};
  pointer-events: ${({ $isHovered, $isSelected }) =>
    $isHovered || $isSelected ? 'auto' : 'none'};
  z-index: ${({ $isHovered, $isSelected }) =>
    $isSelected ? 1002 : $isHovered ? 1001 : 1000};
`;

const WindowInfo = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
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

const AppIcon = styled.img`
  width: 64px;
  height: 64px;
  border-radius: ${({ theme }) => theme.borderRadius.md};
  object-fit: contain;
`;

const WindowName = styled.h2`
  font-size: 24px;
  font-weight: 700;
  color: ${({ theme }) => theme.colors.text.primary};
  max-width: 400px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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
  z-index: 2000;

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
  z-index: 2000;

  &:hover {
    background: ${({ theme }) => theme.colors.status.recording};
    border-color: ${({ theme }) => theme.colors.status.recording};
    transform: scale(1.1);
  }
`;

interface WindowInfo {
  id: string;
  name: string;
  thumbnail: string;
  appIcon?: string;
  windowNumber?: number;
  ownerName?: string;
  pid?: number;
  bounds?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}

interface WindowSelectionOverlayProps {
  windows: WindowInfo[];
  onSelect: (window: WindowInfo) => Promise<void>;
  onClose: () => void;
}

const WindowSelectionOverlay: React.FC<WindowSelectionOverlayProps> = ({
  windows,
  onSelect,
  onClose,
}) => {
  const [hoveredWindow, setHoveredWindow] = useState<WindowInfo | null>(null);
  const [selectedWindow, setSelectedWindow] = useState<WindowInfo | null>(null);

  useEffect(() => {
    let rafId: number | null = null;
    let lastX = -1;
    let lastY = -1;

    const handleMouseMove = (e: MouseEvent) => {
      lastX = e.clientX;
      lastY = e.clientY;

      // Use requestAnimationFrame to throttle hit-testing
      if (rafId === null) {
        rafId = requestAnimationFrame(async () => {
          rafId = null;

          // Use native hit-testing to find the topmost window at cursor position
          // This ensures we only highlight foreground windows, respecting z-order
          const hitWindow = await window.electronAPI.hitTestWindow(lastX, lastY);

          if (hitWindow && 'windowNumber' in hitWindow) {
            // Find matching window in our list
            const matchingWindow = windows.find((win) => {
              // Match by window number or bounds
              return (
                ('windowNumber' in win && win.windowNumber === hitWindow.windowNumber) ||
                (win.bounds &&
                  Math.abs(win.bounds.x - hitWindow.bounds.x) < 1 &&
                  Math.abs(win.bounds.y - hitWindow.bounds.y) < 1)
              );
            });

            setHoveredWindow(matchingWindow || null);
          } else {
            setHoveredWindow(null);
          }
        });
      }
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      if (rafId !== null) {
        cancelAnimationFrame(rafId);
      }
    };
  }, [windows]);

  const handleWindowClick = (window: WindowInfo) => {
    setSelectedWindow(window);
  };

  const handleStartRecording = () => {
    if (selectedWindow) {
      onSelect(selectedWindow);
    }
  };

  return (
    <FullscreenContainer>
      <CloseButton onClick={onClose}>
        <CloseIcon size={20} />
      </CloseButton>

      {windows.map((window) => {
        if (!window.bounds) return null;

        const isHovered = hoveredWindow?.id === window.id;
        const isSelected = selectedWindow?.id === window.id;

        return (
          <WindowOverlay
            key={window.id}
            $bounds={window.bounds}
            $isHovered={isHovered}
            $isSelected={isSelected}
            onClick={() => handleWindowClick(window)}
          >
            {(isHovered || isSelected) && (
              <WindowInfo>
                <AppIcon src={window.appIcon || window.thumbnail} alt={window.name} />
                <WindowName>{window.name}</WindowName>
              </WindowInfo>
            )}
          </WindowOverlay>
        );
      })}

      {selectedWindow && (
        <StartButton onClick={handleStartRecording}>
          Start recording
        </StartButton>
      )}
    </FullscreenContainer>
  );
};

export default WindowSelectionOverlay;

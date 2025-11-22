import React, { useState } from 'react';
import styled from 'styled-components';
import { useRecordingStore } from '../store';
import {
  DisplayIcon,
  WindowIcon,
  AreaIcon,
  DeviceIcon,
  CameraIcon,
  CameraOffIcon,
  MicIcon,
  MicOffIcon,
  SettingsIcon,
} from './Icons';

const Container = styled.div`
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  -webkit-app-region: drag;
`;

const BarContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: ${({ theme }) => theme.colors.background.glass};
  backdrop-filter: blur(20px);
  border: 1px solid ${({ theme }) => theme.colors.border.primary};
  border-radius: ${({ theme }) => theme.borderRadius.full};
  animation: fadeIn 0.3s ease-out;
  -webkit-app-region: drag;
`;

const Divider = styled.div`
  width: 1px;
  height: 24px;
  background: ${({ theme }) => theme.colors.border.primary};
  margin: 0 4px;
  -webkit-app-region: drag;
`;

const Button = styled.button<{ $active?: boolean }>`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 8px 16px;
  background: ${({ $active, theme }) =>
    $active ? theme.colors.accent.primary : 'transparent'};
  color: ${({ theme }) => theme.colors.text.primary};
  border-radius: ${({ theme }) => theme.borderRadius.md};
  font-size: 11px;
  font-weight: 500;
  transition: all ${({ theme }) => theme.transitions.fast};
  position: relative;
  overflow: hidden;
  -webkit-app-region: no-drag;

  &:hover {
    background: ${({ $active, theme }) =>
      $active ? theme.colors.accent.hover : theme.colors.background.tertiary};
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0);
  }

  &::before {
    content: '';
    position: absolute;
    inset: 0;
    opacity: 0;
    background: linear-gradient(
      45deg,
      transparent 30%,
      rgba(255, 255, 255, 0.1) 50%,
      transparent 70%
    );
    transition: opacity ${({ theme }) => theme.transitions.fast};
  }

  &:hover::before {
    opacity: 1;
  }
`;

const IconButton = styled.button<{ $active?: boolean }>`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: ${({ $active, theme }) =>
    $active ? theme.colors.accent.primary : 'transparent'};
  color: ${({ theme }) => theme.colors.text.primary};
  border-radius: ${({ theme }) => theme.borderRadius.md};
  transition: all ${({ theme }) => theme.transitions.fast};
  position: relative;
  -webkit-app-region: no-drag;

  &:hover {
    background: ${({ $active, theme }) =>
      $active ? theme.colors.accent.hover : theme.colors.background.tertiary};
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0);
  }

  svg {
    width: 18px;
    height: 18px;
  }
`;

const IconWrapper = styled.span`
  display: flex;
  align-items: center;
  justify-content: center;
  -webkit-app-region: no-drag;
`;

const ControlBar: React.FC = () => {
  const { micEnabled, cameraEnabled, toggleMic, toggleCamera } = useRecordingStore();
  const [selectedMode, setSelectedMode] = useState<string | null>(null);

  const handleModeClick = (mode: 'area' | 'window' | 'display') => {
    setSelectedMode(mode);
    window.electronAPI.openSelection(mode);
  };

  return (
    <Container>
      <BarContainer>
        <Button
          onClick={() => handleModeClick('display')}
          $active={selectedMode === 'display'}
        >
          <IconWrapper>
            <DisplayIcon size={20} />
          </IconWrapper>
          <span>Display</span>
        </Button>

        <Button
          onClick={() => handleModeClick('window')}
          $active={selectedMode === 'window'}
        >
          <IconWrapper>
            <WindowIcon size={20} />
          </IconWrapper>
          <span>Window</span>
        </Button>

        <Button
          onClick={() => handleModeClick('area')}
          $active={selectedMode === 'area'}
        >
          <IconWrapper>
            <AreaIcon size={20} />
          </IconWrapper>
          <span>Area</span>
        </Button>

        <Button onClick={() => handleModeClick('display')}>
          <IconWrapper>
            <DeviceIcon size={20} />
          </IconWrapper>
          <span>Device</span>
        </Button>

        <Divider />

        <IconButton $active={!cameraEnabled} title="No camera">
          <CameraOffIcon size={20} />
        </IconButton>

        <IconButton $active={cameraEnabled} onClick={toggleCamera} title="Toggle camera">
          <CameraIcon size={20} />
        </IconButton>

        <Divider />

        <IconButton $active={micEnabled} onClick={toggleMic} title="Toggle microphone">
          {micEnabled ? <MicIcon size={20} /> : <MicOffIcon size={20} />}
        </IconButton>

        <Divider />

        <IconButton title="Settings">
          <SettingsIcon size={20} />
        </IconButton>
      </BarContainer>
    </Container>
  );
};

export default ControlBar;

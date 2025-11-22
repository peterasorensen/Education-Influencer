import React, { useState } from 'react';
import styled from 'styled-components';
import { useRecordingStore } from '../store';
import {
  DisplayIcon,
  WindowIcon,
  AreaIcon,
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

const Divider = styled.div`
  width: 1px;
  height: 24px;
  background: ${({ theme }) => theme.colors.border.primary};
  margin: 0 4px;
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
  border: none;
  border-radius: ${({ theme }) => theme.borderRadius.md};
  font-size: 11px;
  font-weight: 500;
  cursor: pointer;
  transition: all ${({ theme }) => theme.transitions.fast};
  position: relative;
  overflow: hidden;

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
  border: none;
  border-radius: ${({ theme }) => theme.borderRadius.md};
  cursor: pointer;
  transition: all ${({ theme }) => theme.transitions.fast};
  position: relative;

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
`;

interface ControlBarProps {
  onModeSelect?: (mode: 'area' | 'window' | 'display') => void;
}

const ControlBar: React.FC<ControlBarProps> = ({ onModeSelect }) => {
  const { micEnabled, toggleMic } = useRecordingStore();
  const [selectedMode, setSelectedMode] = useState<string | null>(null);

  const handleModeClick = (mode: 'area' | 'window' | 'display') => {
    setSelectedMode(mode);
    if (onModeSelect) {
      onModeSelect(mode);
    }
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

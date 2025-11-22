import React, { useState } from 'react';
import { ThemeProvider } from 'styled-components';
import { GlobalStyles } from './GlobalStyles';
import { theme } from './theme';
import VideoEditor from './components/VideoEditor';
import RecordingExample from './RecordingExample';
import styled from 'styled-components';

const AppModeSelector = styled.div`
  position: fixed;
  top: 20px;
  left: 20px;
  z-index: 1000;
  display: flex;
  gap: 8px;
  background: ${theme.colors.background.glass};
  backdrop-filter: blur(10px);
  border: 1px solid ${theme.colors.border.primary};
  border-radius: ${theme.borderRadius.md};
  padding: 4px;
  box-shadow: ${theme.shadows.lg};
`;

const ModeButton = styled.button<{ $active: boolean }>`
  padding: 8px 16px;
  border-radius: ${theme.borderRadius.sm};
  background: ${({ $active }) =>
    $active ? theme.colors.accent.primary : 'transparent'};
  color: ${theme.colors.text.primary};
  border: none;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all ${theme.transitions.fast};

  &:hover {
    background: ${({ $active }) =>
      $active ? theme.colors.accent.hover : theme.colors.background.tertiary};
  }
`;

type AppMode = 'record' | 'edit';

export const VideoEditorApp: React.FC = () => {
  const [mode, setMode] = useState<AppMode>('edit');

  return (
    <ThemeProvider theme={theme}>
      <GlobalStyles />
      <AppModeSelector>
        <ModeButton
          $active={mode === 'record'}
          onClick={() => setMode('record')}
        >
          Record
        </ModeButton>
        <ModeButton
          $active={mode === 'edit'}
          onClick={() => setMode('edit')}
        >
          Edit
        </ModeButton>
      </AppModeSelector>

      {mode === 'record' ? <RecordingExample /> : <VideoEditor />}
    </ThemeProvider>
  );
};

export default VideoEditorApp;

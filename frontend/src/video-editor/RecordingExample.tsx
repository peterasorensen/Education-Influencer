import React, { useState } from 'react';
import { ThemeProvider } from 'styled-components';
import { theme } from './theme';
import StartScreen from './components/StartScreen';
import ControlBar from './components/ControlBar';
import SelectionWindow from './components/SelectionWindow';
import RecordingToolbar from './components/RecordingToolbar';

/**
 * Example component demonstrating how to use the recording components.
 *
 * Flow:
 * 1. StartScreen - Choose between Record or Edit
 * 2. ControlBar - Select recording mode (Display/Window/Area)
 * 3. SelectionWindow - For area mode, draw selection; for others, browser picker
 * 4. RecordingToolbar - Control recording (pause/resume/stop)
 * 5. onFinish callback receives the recorded blob
 */

type RecordingView = 'start' | 'control-bar' | 'selection' | 'recording';

export const RecordingExample: React.FC = () => {
  const [currentView, setCurrentView] = useState<RecordingView>('start');
  const [recordingMode, setRecordingMode] = useState<'area' | 'window' | 'display' | null>(null);

  const handleScreenRecord = () => {
    setCurrentView('control-bar');
  };

  const handleEdit = () => {
    // Navigate to editor
    console.log('Navigate to editor');
  };

  const handleModeSelect = (mode: 'area' | 'window' | 'display') => {
    setRecordingMode(mode);
    setCurrentView('selection');
  };

  const handleStartRecording = () => {
    setCurrentView('recording');
  };

  const handleCloseSelection = () => {
    setCurrentView('control-bar');
  };

  const handleFinishRecording = (blob: Blob) => {
    console.log('Recording finished! Blob size:', blob.size);

    // Example: Create download link
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `recording-${Date.now()}.webm`;
    a.click();
    URL.revokeObjectURL(url);

    // Reset to start
    setCurrentView('start');
    setRecordingMode(null);
  };

  const handleCancelRecording = () => {
    setCurrentView('control-bar');
    setRecordingMode(null);
  };

  return (
    <ThemeProvider theme={theme}>
      <div style={{ width: '100vw', height: '100vh', background: '#0a0a0a' }}>
        {currentView === 'start' && (
          <StartScreen
            onScreenRecord={handleScreenRecord}
            onEdit={handleEdit}
          />
        )}

        {currentView === 'control-bar' && (
          <ControlBar onModeSelect={handleModeSelect} />
        )}

        {currentView === 'selection' && recordingMode && (
          <SelectionWindow
            mode={recordingMode}
            onClose={handleCloseSelection}
            onStartRecording={handleStartRecording}
          />
        )}

        {currentView === 'recording' && (
          <RecordingToolbar
            autoStart={true}
            onFinish={handleFinishRecording}
            onCancel={handleCancelRecording}
          />
        )}
      </div>
    </ThemeProvider>
  );
};

export default RecordingExample;

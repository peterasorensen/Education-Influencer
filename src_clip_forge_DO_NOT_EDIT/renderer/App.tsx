import React, { useEffect, useState } from 'react';
import { ThemeProvider } from 'styled-components';
import { theme } from './theme';
import { GlobalStyles } from './GlobalStyles';
import StartScreen from './components/StartScreen';
import ControlBar from './components/ControlBar';
import SelectionWindow from './components/SelectionWindow';
import RecordingToolbar from './components/RecordingToolbar';
import VideoEditor from './components/VideoEditor';

type ViewMode = 'start-screen' | 'control-bar' | 'selection' | 'recording-toolbar' | 'editor';

const App: React.FC = () => {
  const [viewMode, setViewMode] = useState<ViewMode>('start-screen');
  const [selectionMode, setSelectionMode] = useState<'area' | 'window' | 'display'>('area');

  useEffect(() => {
    // Determine which view to show based on URL hash
    const hash = window.location.hash;

    if (hash.startsWith('#selection/')) {
      const mode = hash.split('/')[1] as 'area' | 'window' | 'display';
      setSelectionMode(mode);
      setViewMode('selection');
    } else if (hash === '#recording-toolbar') {
      setViewMode('recording-toolbar');
    } else if (hash === '#editor') {
      setViewMode('editor');
    } else if (hash === '#control-bar') {
      setViewMode('control-bar');
    } else {
      setViewMode('start-screen');
    }

    // Listen for hash changes
    const handleHashChange = () => {
      const newHash = window.location.hash;
      if (newHash.startsWith('#selection/')) {
        const mode = newHash.split('/')[1] as 'area' | 'window' | 'display';
        setSelectionMode(mode);
        setViewMode('selection');
      } else if (newHash === '#recording-toolbar') {
        setViewMode('recording-toolbar');
      } else if (newHash === '#editor') {
        setViewMode('editor');
      } else if (newHash === '#control-bar') {
        setViewMode('control-bar');
      } else {
        setViewMode('start-screen');
      }
    };

    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  return (
    <ThemeProvider theme={theme}>
      <GlobalStyles />
      {viewMode === 'start-screen' && <StartScreen />}
      {viewMode === 'control-bar' && <ControlBar />}
      {viewMode === 'selection' && <SelectionWindow mode={selectionMode} />}
      {viewMode === 'recording-toolbar' && <RecordingToolbar />}
      {viewMode === 'editor' && <VideoEditor />}
    </ThemeProvider>
  );
};

export default App;

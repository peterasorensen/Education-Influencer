import React from 'react';
import ReactDOM from 'react-dom/client';
import { VideoEditorApp } from './video-editor/VideoEditorApp';

// This is a standalone entry point for the video editor
// You can run it separately or integrate it into the main app

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <VideoEditorApp />
  </React.StrictMode>
);

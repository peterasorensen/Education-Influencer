# Web Adaptations Summary

This document outlines the key adaptations made to convert Electron-based recording components to web-compatible versions.

## Created Files

### Core Components (4 files)
1. `/src/video-editor/components/StartScreen.tsx` - Initial screen with Record/Edit choice
2. `/src/video-editor/components/ControlBar.tsx` - Recording mode selector
3. `/src/video-editor/components/RecordingToolbar.tsx` - Active recording controls
4. `/src/video-editor/components/SelectionWindow.tsx` - Area selection interface

### Supporting Infrastructure
5. `/src/video-editor/store/index.ts` - Zustand state management
6. `/src/video-editor/theme/index.ts` - Styled-components theme
7. `/src/video-editor/hooks/useRecording.ts` - Recording lifecycle hook
8. `/src/video-editor/index.ts` - Main export file
9. `/src/video-editor/components/index.ts` - Component exports

### Documentation & Examples
10. `/src/video-editor/RecordingExample.tsx` - Complete usage example
11. `/src/video-editor/RECORDING_COMPONENTS.md` - Comprehensive documentation
12. `/src/video-editor/WEB_ADAPTATIONS.md` - This file

## Key Adaptations Made

### 1. Screen Capture API Change
**Before (Electron):**
```typescript
// Required explicit source selection from desktopCapturer
const sources = await window.electronAPI.getSources();
const constraints = {
  video: {
    mandatory: {
      chromeMediaSource: 'desktop',
      chromeMediaSourceId: selectedSource.id,
    },
  },
};
const stream = await navigator.mediaDevices.getUserMedia(constraints);
```

**After (Web):**
```typescript
// Uses browser's native picker
const stream = await navigator.mediaDevices.getDisplayMedia({
  video: { displaySurface: 'monitor' },
  audio: false,
});
```

### 2. Window/Display Selection
**Before (Electron):**
- Custom overlay components (DisplaySelectionOverlay, WindowSelectionOverlay)
- Showed thumbnails of all available windows/displays
- Required IPC communication with main process

**After (Web):**
- Uses browser's built-in picker (automatically shown by `getDisplayMedia()`)
- SelectionWindow auto-triggers recording for window/display modes
- Simpler but less customizable

### 3. Area Selection
**Before (Electron):**
- Separate BrowserWindow created as fullscreen overlay
- Complex window management and IPC

**After (Web):**
- Fixed position fullscreen div overlay
- Mouse event handlers for drawing selection rectangle
- Stores coordinates in Zustand store

**Implementation:**
```typescript
const SelectionBox = styled.div<{ $x, $y, $width, $height }>`
  position: absolute;
  left: ${({ $x }) => $x}px;
  top: ${({ $y }) => $y}px;
  width: ${({ $width }) => $width}px;
  height: ${({ $height }) => $height}px;
  border: 3px solid ${({ theme }) => theme.colors.accent.primary};
  box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.4);
`;
```

### 4. Removed Electron-Specific Features
- `window.electronAPI.*` calls replaced with direct browser APIs
- `-webkit-app-region: drag` styles (for frameless window dragging)
- `window.location.hash` navigation (use React state instead)
- Camera preview (not core to screen recording)
- Device recording mode (redundant with Display)

### 5. State Management
**Before (Electron):**
- Store in renderer process
- IPC for passing recording config between windows

**After (Web):**
- Zustand store accessible across all components
- Direct prop passing and callbacks
- No IPC needed

### 6. Component Props Added
All components now accept callback props for integration:
- `StartScreen`: `onScreenRecord`, `onEdit`
- `ControlBar`: `onModeSelect`
- `SelectionWindow`: `onClose`, `onStartRecording`
- `RecordingToolbar`: `onFinish`, `onCancel`, `autoStart`

### 7. Recording Flow Simplification
**Before (Electron):**
1. User clicks mode → IPC to main
2. Main opens selection window
3. Selection window sends config via IPC
4. Main opens recording toolbar window
5. Toolbar loads config from main process

**After (Web):**
1. User clicks mode → State updated
2. Show SelectionWindow component
3. SelectionWindow triggers callback
4. Show RecordingToolbar component
5. Auto-start recording with existing state

## Browser API Usage

### MediaRecorder
```typescript
const recorder = new MediaRecorder(stream, {
  mimeType: 'video/webm;codecs=vp9',
  videoBitsPerSecond: 8000000,
});

recorder.ondataavailable = (event) => {
  if (event.data?.size > 0) {
    addRecordedChunk(event.data);
  }
};

recorder.start(1000); // 1-second chunks
```

### Microphone Integration
```typescript
const audioStream = await navigator.mediaDevices.getUserMedia({
  audio: {
    echoCancellation: true,
    noiseSuppression: true,
    sampleRate: 44100,
  },
});

// Combine with video
const combinedStream = new MediaStream([
  videoStream.getVideoTracks()[0],
  audioStream.getAudioTracks()[0],
]);
```

## Styling Approach

Maintained original styled-components approach with theme:
- Glass morphism backgrounds with `backdrop-filter: blur(20px)`
- Smooth animations and transitions
- Purple gradient accent colors (#7c3aed)
- Dark theme (#0a0a0a background)

All animations use CSS instead of JavaScript for better performance.

## Notable Limitations

1. **Area cropping**: Coordinates are stored but actual video cropping must be done during export (browser MediaRecorder can't crop live streams)
2. **System audio**: Cannot capture in most browsers (security restriction)
3. **Custom window thumbnails**: Uses browser's native picker instead
4. **Multi-display**: Handled by browser picker, not customizable

## Integration Example

```typescript
import { RecordingExample } from './video-editor';

function App() {
  return <RecordingExample />;
}
```

Or build your own flow:
```typescript
import {
  StartScreen,
  ControlBar,
  SelectionWindow,
  RecordingToolbar
} from './video-editor';

// Manage state and render appropriate component based on flow
```

## Dependencies Required

```json
{
  "dependencies": {
    "react": "^18.0.0",
    "styled-components": "^6.0.0",
    "zustand": "^4.0.0"
  },
  "devDependencies": {
    "@types/styled-components": "^5.1.26"
  }
}
```

## Browser Compatibility

- Chrome 72+ (getDisplayMedia)
- Firefox 66+ (getDisplayMedia)
- Safari 13+ (getDisplayMedia)
- Edge 79+ (Chromium-based)

Not supported: IE11, older mobile browsers

## Next Steps

To use these components in your app:
1. Install dependencies (styled-components, zustand)
2. Import `RecordingExample` or individual components
3. Wrap with `ThemeProvider` if using individual components
4. Handle the `onFinish` blob (save/upload/process)
5. Optional: Implement video cropping for area selection mode

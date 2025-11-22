# Web-Adapted Recording Components

Web-based screen recording components adapted from the Electron-based Clip Forge application. These components use browser APIs (`getDisplayMedia` and `getUserMedia`) instead of Electron's desktop capture.

## Components

### 1. StartScreen
Initial choice screen for users to select between recording or editing.

**Location:** `/src/video-editor/components/StartScreen.tsx`

**Props:**
- `onScreenRecord?: () => void` - Callback when "Screen Record" is clicked
- `onEdit?: () => void` - Callback when "Edit" is clicked

### 2. ControlBar
Recording mode selector with options for Display, Window, or Area recording.

**Location:** `/src/video-editor/components/ControlBar.tsx`

**Props:**
- `onModeSelect?: (mode: 'area' | 'window' | 'display') => void` - Callback when a mode is selected

**Features:**
- Display mode - Capture entire screen(s)
- Window mode - Capture specific window (uses browser picker)
- Area mode - Select custom screen area
- Microphone toggle

### 3. SelectionWindow
Handles area selection or triggers browser's native display/window picker.

**Location:** `/src/video-editor/components/SelectionWindow.tsx`

**Props:**
- `mode: 'area' | 'window' | 'display'` - Recording mode
- `onClose?: () => void` - Callback when selection is cancelled
- `onStartRecording?: () => void` - Callback when ready to start recording

**Behavior by Mode:**
- **Area mode:** Displays fullscreen overlay where user can draw selection rectangle
- **Window/Display mode:** Automatically triggers browser's native picker via `getDisplayMedia()`

### 4. RecordingToolbar
Floating toolbar during active recording with controls.

**Location:** `/src/video-editor/components/RecordingToolbar.tsx`

**Props:**
- `onFinish?: (blob: Blob) => void` - Callback when recording finishes successfully
- `onCancel?: () => void` - Callback when recording is cancelled
- `autoStart?: boolean` - Whether to automatically start recording on mount

**Features:**
- Real-time timer display
- Pause/Resume recording
- Restart recording
- Finish (stop and save)
- Cancel (discard)

## Supporting Files

### Store
**Location:** `/src/video-editor/store/index.ts`

Zustand store managing recording state:
- Recording status and time
- Selected area/mode
- Media streams and recorder
- Recorded chunks
- Microphone/camera toggles

### Theme
**Location:** `/src/video-editor/theme/index.ts`

Styled-components theme with colors, shadows, borders, and transitions.

### Icons
**Location:** `/src/video-editor/components/Icons.tsx`

SVG icon components used throughout the recording UI.

### Hooks
**Location:** `/src/video-editor/hooks/useRecording.ts`

Custom hook for managing recording lifecycle:
- `startRecording()` - Initialize and start screen capture
- `stopRecording()` - Stop and cleanup streams
- Uses `getDisplayMedia()` for screen capture
- Uses `getUserMedia()` for microphone audio

## Usage Example

See `/src/video-editor/RecordingExample.tsx` for a complete implementation example.

```tsx
import { ThemeProvider } from 'styled-components';
import { theme } from './theme';
import StartScreen from './components/StartScreen';
import ControlBar from './components/ControlBar';
import SelectionWindow from './components/SelectionWindow';
import RecordingToolbar from './components/RecordingToolbar';

// 1. Show StartScreen
<StartScreen
  onScreenRecord={() => setView('control-bar')}
/>

// 2. Show ControlBar
<ControlBar
  onModeSelect={(mode) => {
    setMode(mode);
    setView('selection');
  }}
/>

// 3. Show SelectionWindow
<SelectionWindow
  mode={mode}
  onStartRecording={() => setView('recording')}
  onClose={() => setView('control-bar')}
/>

// 4. Show RecordingToolbar
<RecordingToolbar
  autoStart={true}
  onFinish={(blob) => {
    // Save or process recording
    const url = URL.createObjectURL(blob);
    // Download or upload blob
  }}
  onCancel={() => setView('start')}
/>
```

## Key Differences from Electron Version

### Screen Capture
- **Electron:** Uses `desktopCapturer` API with explicit source selection
- **Web:** Uses `getDisplayMedia()` which shows browser's native picker

### Window/Display Selection
- **Electron:** Custom overlays showing thumbnails of all windows/displays
- **Web:** Browser's built-in picker (simpler but less customizable)

### Area Selection
- **Electron:** Creates separate fullscreen window for selection
- **Web:** Uses fixed fullscreen overlay div with selection rectangle

### Removed Features
- Camera preview (not core to screen recording)
- Device recording mode (redundant with Display mode)
- Electron-specific window controls

### Recording Format
- Uses MediaRecorder API with WebM container
- VP9 codec preferred, VP8 fallback
- 8 Mbps video bitrate (5 Mbps for VP8)
- Optional microphone audio mixing

## Browser Compatibility

Requires modern browser with support for:
- `navigator.mediaDevices.getDisplayMedia()` (Chrome 72+, Firefox 66+, Safari 13+)
- `MediaRecorder` API (Chrome 47+, Firefox 25+, Safari 14+)
- VP9 or VP8 codec support

## Limitations

1. **Area selection cropping:** The area selection stores coordinates but actual cropping would need to be done during export/processing (browser can't crop live streams)
2. **System audio:** Cannot capture system audio in most browsers (security restriction)
3. **Multiple displays:** Browser picker handles multi-display selection
4. **Window preview:** No custom window thumbnails (uses browser's picker)

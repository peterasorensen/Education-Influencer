# Quick Start Guide

Get started with the web-adapted recording components in 5 minutes.

## Prerequisites

All required dependencies are already installed in this project:
- ✓ React 19.1.1
- ✓ styled-components 6.1.19
- ✓ zustand 5.0.8

## Option 1: Use the Example (Fastest)

### Step 1: Import the Example
```typescript
import { RecordingExample } from './video-editor';
```

### Step 2: Add to Your App
```typescript
function App() {
  return <RecordingExample />;
}
```

### Step 3: Run
```bash
npm run dev
```

That's it! Open your browser and try recording.

## Option 2: Build Your Own Flow

### Step 1: Import Components
```typescript
import { useState } from 'react';
import { ThemeProvider } from 'styled-components';
import {
  StartScreen,
  ControlBar,
  SelectionWindow,
  RecordingToolbar,
  theme
} from './video-editor';
```

### Step 2: Create State
```typescript
type View = 'start' | 'control-bar' | 'selection' | 'recording';

function MyRecordingApp() {
  const [view, setView] = useState<View>('start');
  const [mode, setMode] = useState<'area' | 'window' | 'display' | null>(null);

  // ... handlers
}
```

### Step 3: Create Handlers
```typescript
const handleScreenRecord = () => setView('control-bar');

const handleModeSelect = (selectedMode: 'area' | 'window' | 'display') => {
  setMode(selectedMode);
  setView('selection');
};

const handleStartRecording = () => setView('recording');

const handleFinish = (blob: Blob) => {
  // Save the recording
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `recording-${Date.now()}.webm`;
  a.click();
  URL.revokeObjectURL(url);

  // Reset
  setView('start');
  setMode(null);
};

const handleCancel = () => {
  setView('control-bar');
  setMode(null);
};
```

### Step 4: Render Components
```typescript
return (
  <ThemeProvider theme={theme}>
    <div style={{ width: '100vw', height: '100vh', background: '#0a0a0a' }}>
      {view === 'start' && (
        <StartScreen onScreenRecord={handleScreenRecord} />
      )}

      {view === 'control-bar' && (
        <ControlBar onModeSelect={handleModeSelect} />
      )}

      {view === 'selection' && mode && (
        <SelectionWindow
          mode={mode}
          onStartRecording={handleStartRecording}
          onClose={() => setView('control-bar')}
        />
      )}

      {view === 'recording' && (
        <RecordingToolbar
          autoStart
          onFinish={handleFinish}
          onCancel={handleCancel}
        />
      )}
    </div>
  </ThemeProvider>
);
```

## Option 3: Direct Store Access

For more control, use the Zustand store directly:

```typescript
import { useRecordingStore } from './video-editor';

function CustomRecorder() {
  const {
    isRecording,
    recordingTime,
    micEnabled,
    toggleMic,
    reset
  } = useRecordingStore();

  return (
    <div>
      <p>Recording: {isRecording ? 'Yes' : 'No'}</p>
      <p>Time: {recordingTime}s</p>
      <button onClick={toggleMic}>
        Mic: {micEnabled ? 'On' : 'Off'}
      </button>
      <button onClick={reset}>Reset</button>
    </div>
  );
}
```

## Common Use Cases

### Save Recording to Server

```typescript
const handleFinish = async (blob: Blob) => {
  const formData = new FormData();
  formData.append('video', blob, 'recording.webm');

  await fetch('/api/upload', {
    method: 'POST',
    body: formData
  });
};
```

### Convert to Different Format

```typescript
// Using FFmpeg (install @ffmpeg/ffmpeg first)
import { FFmpeg } from '@ffmpeg/ffmpeg';

const handleFinish = async (blob: Blob) => {
  const ffmpeg = new FFmpeg();
  await ffmpeg.load();

  const data = await blob.arrayBuffer();
  await ffmpeg.writeFile('input.webm', new Uint8Array(data));
  await ffmpeg.exec(['-i', 'input.webm', 'output.mp4']);

  const output = await ffmpeg.readFile('output.mp4');
  // ... save or download output
};
```

### Preview Before Saving

```typescript
const [recordedBlob, setRecordedBlob] = useState<Blob | null>(null);
const [previewUrl, setPreviewUrl] = useState<string | null>(null);

const handleFinish = (blob: Blob) => {
  setRecordedBlob(blob);
  setPreviewUrl(URL.createObjectURL(blob));
  setView('preview');
};

// In render:
{view === 'preview' && previewUrl && (
  <div>
    <video src={previewUrl} controls />
    <button onClick={() => {
      // Download
      const a = document.createElement('a');
      a.href = previewUrl;
      a.download = 'recording.webm';
      a.click();
    }}>
      Download
    </button>
    <button onClick={() => {
      URL.revokeObjectURL(previewUrl);
      setView('start');
    }}>
      New Recording
    </button>
  </div>
)}
```

### Add Custom Styling

```typescript
import { ThemeProvider } from 'styled-components';

const myTheme = {
  ...theme,
  colors: {
    ...theme.colors,
    accent: {
      primary: '#3b82f6', // Blue instead of purple
      hover: '#2563eb',
    }
  }
};

<ThemeProvider theme={myTheme}>
  <RecordingExample />
</ThemeProvider>
```

## Testing the Flow

1. **Start Screen**: Click "Screen Record"
2. **Control Bar**:
   - Try each mode (Display, Window, Area)
   - Toggle microphone on/off
3. **Area Selection** (if Area mode):
   - Draw a rectangle on screen
   - See dimensions update
   - Click "Start Recording"
4. **Window/Display Mode**:
   - Browser picker appears
   - Select screen/window
   - Recording starts automatically
5. **Recording Toolbar**:
   - Timer counts up
   - Try pause/resume
   - Try restart
   - Click "Finish" to save

## Browser Testing

Test in these browsers:
- ✓ Chrome 72+ (Recommended)
- ✓ Firefox 66+
- ✓ Edge 79+
- ✓ Safari 13+

## Troubleshooting

### Recording doesn't start
- Check browser permissions for screen capture
- Ensure HTTPS (required for getDisplayMedia)
- Check console for errors

### No audio captured
- Verify microphone permission granted
- Check microphone toggle is enabled
- System audio capture not supported in browsers

### Video file is empty
- Ensure recording runs for at least 1 second
- Check browser codec support (VP9 or VP8)
- Verify chunks are being captured (check console logs)

### Area selection not showing
- Ensure mode is set to 'area'
- Check z-index of overlay
- Verify fullscreen styles applied

## Performance Tips

1. **Use VP9 codec** (better compression, smaller files)
2. **Limit recording time** for memory management
3. **Use 1-second chunks** (already configured)
4. **Stop unused streams** (handled automatically)
5. **Clean up blob URLs** after use

```typescript
// Always clean up
useEffect(() => {
  return () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
  };
}, [previewUrl]);
```

## Next Steps

- Read [RECORDING_COMPONENTS.md](./RECORDING_COMPONENTS.md) for detailed API docs
- See [WEB_ADAPTATIONS.md](./WEB_ADAPTATIONS.md) for technical details
- Check [COMPONENT_FLOW.md](./COMPONENT_FLOW.md) for architecture
- Review [RecordingExample.tsx](./RecordingExample.tsx) for implementation

## Getting Help

Common issues and solutions:

| Issue | Solution |
|-------|----------|
| TypeScript errors | Ensure all imports match created files |
| Styled-components warning | Add ThemeProvider wrapper |
| Recording blob is empty | Check browser codec support |
| Microphone not working | Grant browser permissions |
| Area selection not visible | Check z-index and overlay styles |

## Files to Review

1. **Components**: `/src/video-editor/components/`
2. **Store**: `/src/video-editor/store/index.ts`
3. **Theme**: `/src/video-editor/theme/index.ts`
4. **Example**: `/src/video-editor/RecordingExample.tsx`
5. **Docs**: All `.md` files in `/src/video-editor/`

Happy recording!

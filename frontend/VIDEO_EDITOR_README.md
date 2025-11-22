# Web-Based Video Editor

A complete, professional-grade video editor built for the web with feature parity to the Electron-based ClipForge application.

## Features

### 🎬 Recording
- **Screen Capture**: Record your entire screen or specific displays
- **Window Capture**: Record specific application windows (browser native picker)
- **Area Selection**: Draw a custom rectangle to record a specific region
- **Microphone Audio**: Toggle microphone input during recording
- **High Quality**: 8 Mbps bitrate, VP9/VP8 codec support

### ✂️ Video Editing
- **Multi-track Timeline**: Unlimited video and audio tracks
- **Drag & Drop**: Import media and drag to timeline
- **Clip Manipulation**: Move, trim, split, and delete clips
- **Timeline Zoom**: 10-200 pixels/second with slider and pinch gestures
- **Playhead Scrubbing**: Click timeline to jump to any time
- **Adaptive Ruler**: Time markers adjust based on zoom level

### 🔍 Zoom System (Signature Feature)
- **Zoom Segments**: Add zoom effects to specific timeline sections
- **Auto Mode**: Automatically follows cursor position from recordings
- **Manual Mode**: Set custom zoom target with visual position picker
- **Zoom Levels**: 1.0x - 2.0x magnification
- **Smooth Transitions**: Interpolated zoom animations

### 📹 Video Player
- **Aspect Ratios**: Auto, 16:9, 9:16, 4:3, 1:1, 21:9
- **Crop Modes**: Fit (contain) or Fill (cover)
- **Real-time Zoom**: Preview zoom effects during playback
- **Cursor Tracking**: Interpolated cursor positions for smooth auto-zoom
- **Play/Pause**: Click video or use spacebar

### 📚 Media Library
- **Import Formats**:
  - Video: MP4, MOV, AVI, MKV, WebM
  - Audio: MP3, WAV, AAC, OGG, M4A
  - Image: JPG, JPEG, PNG, GIF, WebP
- **Automatic Thumbnails**: Generated for videos and images
- **File Metadata**: Duration, dimensions, file size
- **Drag & Drop**: Import from desktop or drag to timeline
- **Double-click**: Quick add to timeline

### 📤 Export
- **Formats**: MP4 (H.264), WebM (VP9)
- **Quality Presets**: Low, Medium, High, Ultra (CRF-based)
- **Resolutions**: Original, 4K, QHD, Full HD, HD, Custom
- **Browser-based**: Uses FFmpeg.wasm (no server required)
- **Progress Tracking**: Real-time export progress
- **Auto Download**: Finished video downloads automatically

### ⌨️ Keyboard Shortcuts
- **Space**: Play/pause
- **Cmd/Ctrl+Z**: Undo
- **Cmd/Ctrl+Shift+Z**: Redo
- **Delete/Backspace**: Delete selected clips or zoom segments

### 🎨 UI/UX
- **Dark Theme**: Purple accent colors (#7c3aed)
- **Glass Morphism**: Frosted glass backgrounds with blur
- **Collapsible Panels**: Media library and zoom editor
- **Smooth Animations**: Fade, pulse, shimmer effects
- **Custom Scrollbars**: Themed scrollbar styling
- **Responsive**: Adapts to different screen sizes

## Architecture

### Technology Stack
- **React 19**: UI framework
- **TypeScript**: Type safety
- **Zustand**: State management
- **styled-components**: CSS-in-JS styling
- **FFmpeg.wasm**: Browser-based video processing
- **MediaRecorder API**: Screen recording
- **Canvas API**: Thumbnail generation

### File Structure
```
frontend/src/video-editor/
├── components/
│   ├── VideoEditor.tsx          # Main editor layout
│   ├── Timeline.tsx              # Multi-track timeline
│   ├── VideoPlayer.tsx           # Video preview with zoom
│   ├── MediaLibrary.tsx          # Media import & management
│   ├── ZoomEditor.tsx            # Zoom segment editor
│   ├── ExportPanel.tsx           # Export configuration
│   ├── StartScreen.tsx           # Record vs Edit choice
│   ├── ControlBar.tsx            # Recording mode selector
│   ├── RecordingToolbar.tsx      # Active recording controls
│   ├── SelectionWindow.tsx       # Area selection overlay
│   └── Icons.tsx                 # SVG icon components
├── store/
│   └── index.ts                  # Zustand stores (recording, editor)
├── theme/
│   └── index.ts                  # Design system theme
├── hooks/
│   └── useRecording.ts           # Recording lifecycle hook
├── GlobalStyles.tsx              # Global CSS & animations
├── VideoEditorApp.tsx            # App wrapper with mode toggle
├── RecordingExample.tsx          # Recording flow example
└── index.ts                      # Barrel exports
```

### State Management

**Recording Store** (`useRecordingStore`):
```typescript
{
  isRecording: boolean
  isPaused: boolean
  recordingTime: number
  recordingMode: 'area' | 'window' | 'display' | null
  selectedArea: { x, y, width, height } | null
  mediaStream: MediaStream | null
  mediaRecorder: MediaRecorder | null
  recordedChunks: Blob[]
  micEnabled: boolean
}
```

**Editor Store** (`useEditorStore`):
```typescript
{
  mediaItems: MediaItem[]
  tracks: TimelineTrack[]
  currentTime: number
  zoom: number
  isPlaying: boolean
  duration: number
  zoomSegments: ZoomSegment[]
  selectedClipIds: string[]
  exportProgress: number
  history: HistoryState[]
  historyIndex: number
}
```

## Running the Video Editor

### Option 1: Standalone (Recommended for Development)
```bash
cd frontend
npm run dev
```

Then navigate to: `http://localhost:5173/video-editor.html`

### Option 2: Integrated with Main App
Import and use the `VideoEditorApp` component:

```tsx
import { VideoEditorApp } from './video-editor/VideoEditorApp';

function App() {
  return <VideoEditorApp />;
}
```

## Browser Compatibility

### Minimum Requirements
- **Chrome**: 72+ (recommended)
- **Firefox**: 66+
- **Safari**: 13+
- **Edge**: 79+

### Required APIs
- MediaRecorder API (for recording)
- getDisplayMedia() (for screen capture)
- Canvas API (for thumbnails)
- WebAssembly (for FFmpeg.wasm)
- Blob/File APIs (for media handling)

### Security Requirements
For recording to work, the page must be served over:
- `https://` (production)
- `http://localhost` (development)

For SharedArrayBuffer (required by FFmpeg.wasm), these headers are needed:
```
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
```

These are already configured in `vite.config.ts`.

## Usage Guide

### 1. Recording a Video
1. Click **"Record"** mode in the top-left toggle
2. Select recording mode:
   - **Display**: Captures entire screen (browser shows picker)
   - **Window**: Captures specific window (browser shows picker)
   - **Area**: Draw rectangle on screen to select region
3. Toggle microphone if you want audio commentary
4. Click **"Start Recording"**
5. Perform your actions
6. Click **"Finish"** when done
7. Video automatically loads into editor

### 2. Importing Media
1. Click **"+ Import Media"** in Media Library
2. Select video, audio, or image files
3. Thumbnails generate automatically
4. Drag media to timeline or double-click to add

### 3. Editing on Timeline
1. **Add clips**: Drag from media library to track
2. **Move clips**: Click and drag clips horizontally
3. **Trim clips**: Drag left/right edges of clips
4. **Split clips**: Place playhead and press split button
5. **Delete clips**: Select and press Delete/Backspace
6. **Zoom timeline**: Use slider or pinch gesture

### 4. Adding Zoom Effects
1. Click on the **Zooms** timeline row
2. Click where you want zoom to start
3. Drag segment edges to adjust duration
4. Select segment to edit in right panel
5. Adjust zoom level (1.0x - 2.0x)
6. Choose mode:
   - **Auto**: Follows cursor (for recordings)
   - **Manual**: Click position picker to set focus point

### 5. Exporting Video
1. Click **"Export"** button
2. Choose format (MP4 or WebM)
3. Select quality preset (Low/Medium/High/Ultra)
4. Choose resolution or keep original
5. Click **"Export Video"**
6. Wait for processing (progress shown)
7. Video downloads automatically when complete

## Performance Optimization

### Tips for Best Performance
1. **Limit timeline clips**: Keep under 50 clips for smooth playback
2. **Compress large files**: Use smaller source videos when possible
3. **Close other tabs**: Free up browser memory
4. **Use Chrome**: Best WebAssembly performance
5. **Export in smaller resolutions**: Faster processing

### Memory Management
- Blob URLs are automatically cleaned up
- FFmpeg virtual filesystem is cleared after export
- Media thumbnails use efficient canvas rendering
- Timeline uses requestAnimationFrame for smooth dragging

## Known Limitations

1. **Export Formats**: MOV not supported (browser FFmpeg limitation)
2. **File Size**: Large exports (>2GB) may fail in some browsers
3. **Recording**: No system audio capture (browser security)
4. **Camera**: Camera overlay not implemented (not core feature)
5. **Native Window Detection**: Uses browser picker instead of overlay

## Future Enhancements

- [ ] Audio waveform visualization
- [ ] Text/Title tracks
- [ ] Transition effects between clips
- [ ] Video filters and color grading
- [ ] Image clip support on timeline
- [ ] Cloud storage integration
- [ ] Collaborative editing
- [ ] Mobile/touch support

## Troubleshooting

### Recording Not Starting
- Ensure page is served over https:// or localhost
- Check browser permissions for screen capture
- Try refreshing the page

### Export Failing
- Check browser console for errors
- Ensure sufficient memory available
- Try smaller resolution or lower quality
- Close other browser tabs

### Video Not Playing
- Verify file format is supported
- Check browser console for errors
- Ensure video loaded successfully (check media library)

### Performance Issues
- Reduce timeline zoom level
- Close collapsible panels when not needed
- Use smaller source files
- Clear browser cache

## Credits

Adapted from the ClipForge Electron application with full feature parity for web browsers.

**Technologies Used**:
- React, TypeScript, Zustand
- styled-components
- FFmpeg.wasm by @ffmpeg/ffmpeg
- MediaRecorder API
- Canvas API

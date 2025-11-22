# Quick Start Guide - Web Video Editor

Get the video editor running in 3 simple steps!

## Installation

All dependencies are already installed. If starting fresh:

```bash
cd frontend
npm install
```

## Running the Editor

### Option 1: Standalone Video Editor (Recommended)

```bash
npm run dev:editor
```

This will:
- Start the dev server
- Automatically open `http://localhost:5173/video-editor.html`
- Show the video editor with Record/Edit mode toggle

### Option 2: Main App with Access to Editor

```bash
npm run dev
```

Then manually navigate to: `http://localhost:5173/video-editor.html`

## First Steps

### 1. Try Recording
1. Click **"Record"** in the top-left toggle
2. Select **"Display"** or **"Window"** mode
3. Click **"Start Recording"**
4. Browser will ask you to select a screen/window
5. Perform your screen actions
6. Click **"Finish"** when done
7. Recording loads into editor automatically

### 2. Try Editing
1. Click **"Edit"** in the top-left toggle
2. Click **"+ Import Media"** in the left panel
3. Select a video file
4. Drag it to the timeline
5. Click and drag to move it
6. Use the edges to trim
7. Press **Space** to play/pause

### 3. Try Zoom Effects
1. Add a video clip to timeline
2. Look for the **"Zooms"** timeline row below the main track
3. Click on the zoom timeline to add a segment
4. Drag the segment to adjust timing
5. Click the segment to select it
6. Right panel shows zoom controls:
   - Adjust zoom level (1.0x - 2.0x)
   - Toggle Auto/Manual mode
   - For Manual: click position picker to set focus point
7. Press **Space** to preview the zoom effect

### 4. Export Your Video
1. Click **"Export"** button (top right)
2. Choose format: **MP4** (recommended) or WebM
3. Select quality: **High** (recommended)
4. Click **"Export Video"**
5. Wait for processing (progress shown)
6. Video downloads automatically

## Keyboard Shortcuts

- **Space** - Play/pause video
- **Cmd/Ctrl+Z** - Undo
- **Cmd/Ctrl+Shift+Z** - Redo
- **Delete/Backspace** - Delete selected clip or zoom segment

## Building for Production

```bash
npm run build:editor
```

Output files will be in `dist/` folder. Deploy to any static hosting:
- Vercel
- Netlify
- GitHub Pages
- AWS S3 + CloudFront

## File Locations

All video editor code is in:
```
frontend/src/video-editor/
```

Entry points:
- Development: `/video-editor.html`
- Production: `dist/video-editor.html`

## Browser Requirements

**Minimum versions:**
- Chrome 72+ (recommended)
- Firefox 66+
- Safari 13+
- Edge 79+

**Must have:**
- Modern browser with MediaRecorder API
- WebAssembly support (for FFmpeg export)
- HTTPS or localhost (for screen recording)

## Troubleshooting

### "Recording not working"
→ Make sure you're on `localhost` or `https://`

### "Export fails"
→ Check browser console, try lower quality/resolution

### "No audio in recording"
→ Enable microphone toggle before recording

### "Video not playing"
→ Check if file format is supported (MP4, WebM, MOV, etc.)

## Next Steps

1. Read the full documentation: `VIDEO_EDITOR_README.md`
2. Explore the components in `src/video-editor/components/`
3. Check the store for state management: `src/video-editor/store/`
4. Customize the theme: `src/video-editor/theme/`

## Need Help?

Check these files:
- `VIDEO_EDITOR_README.md` - Full documentation
- `src/video-editor/RecordingExample.tsx` - Example implementation
- `src/video-editor/components/` - All component source code

Happy editing! 🎬

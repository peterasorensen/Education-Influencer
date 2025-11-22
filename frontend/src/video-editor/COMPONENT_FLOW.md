# Recording Component Flow

Visual guide to the recording flow and component relationships.

## User Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        START SCREEN                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Clip Forge                              │   │
│  │  [Screen Record]  |  [Edit]                         │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ Click "Screen Record"
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                       CONTROL BAR                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ [Display] [Window] [Area] | [Mic] | [Settings]     │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ Select mode (Display/Window/Area)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    SELECTION WINDOW                          │
│                                                              │
│  Area Mode:                                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Fullscreen overlay with selection rectangle         │   │
│  │  ┌──────────────┐                                    │   │
│  │  │  1920 x 1080 │  ← Dimension label                │   │
│  │  │              │                                    │   │
│  │  │   Selected   │                                    │   │
│  │  │     Area     │                                    │   │
│  │  └──────────────┘                                    │   │
│  │        [Start Recording]                             │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  Window/Display Mode:                                        │
│  → Triggers browser picker → Auto-start recording           │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ Start recording
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   RECORDING TOOLBAR                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ [🗑]  |  ● 00:45  |  [⏸] [↻]  |  [■ Finish]        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  Controls:                                                   │
│  • Trash: Cancel recording                                  │
│  • Timer: Shows elapsed time                                │
│  • Pause: Pause/Resume                                      │
│  • Restart: Discard and start over                         │
│  • Finish: Stop and save recording                         │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ Click "Finish"
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   onFinish(blob: Blob)                       │
│                                                              │
│  • blob: WebM video file                                    │
│  • Can download, upload, or process                         │
│  • Contains video + optional audio                          │
└─────────────────────────────────────────────────────────────┘
```

## State Flow

```
┌──────────────────┐
│  Initial State   │
│                  │
│  recordingMode:  │ null
│  isRecording:    │ false
│  recordedChunks: │ []
│  selectedArea:   │ null
└──────────────────┘
         │
         │ User selects mode
         ▼
┌──────────────────┐
│  Mode Selected   │
│                  │
│  recordingMode:  │ 'area' | 'window' | 'display'
│  isRecording:    │ false
└──────────────────┘
         │
         │ Start recording
         ▼
┌──────────────────┐
│   Recording...   │
│                  │
│  isRecording:    │ true
│  mediaRecorder:  │ MediaRecorder instance
│  recordedChunks: │ [blob, blob, ...]
│  recordingTime:  │ 45 (seconds)
└──────────────────┘
         │
         │ Finish recording
         ▼
┌──────────────────┐
│  Recording Done  │
│                  │
│  isRecording:    │ false
│  recordedChunks: │ Combined into final blob
│  → Reset state   │
└──────────────────┘
```

## Component Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                     RecordingExample                         │
│                  (Parent/Orchestrator)                       │
│                                                              │
│  State:                                                      │
│  • currentView: 'start' | 'control-bar' | 'selection' |     │
│                 'recording'                                  │
│  • recordingMode: 'area' | 'window' | 'display' | null      │
└─────────────────────────────────────────────────────────────┘
         │
         ├─────────────────┬──────────────┬──────────────┐
         ▼                 ▼              ▼              ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ StartScreen  │  │ ControlBar   │  │ Selection    │  │ Recording    │
│              │  │              │  │ Window       │  │ Toolbar      │
│ Props:       │  │ Props:       │  │              │  │              │
│ • onScreen   │  │ • onMode     │  │ Props:       │  │ Props:       │
│   Record     │  │   Select     │  │ • mode       │  │ • autoStart  │
│ • onEdit     │  │              │  │ • onStart    │  │ • onFinish   │
│              │  │              │  │   Recording  │  │ • onCancel   │
│              │  │              │  │ • onClose    │  │              │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
         │                 │              │              │
         └─────────────────┴──────────────┴──────────────┘
                          │
                          ▼
            ┌──────────────────────────┐
            │  useRecordingStore       │
            │  (Zustand State)         │
            │                          │
            │  • recordingMode         │
            │  • isRecording           │
            │  • isPaused              │
            │  • recordingTime         │
            │  • mediaRecorder         │
            │  • recordedChunks        │
            │  • micEnabled            │
            └──────────────────────────┘
                          │
                          ▼
            ┌──────────────────────────┐
            │  useRecording Hook       │
            │                          │
            │  • startRecording()      │
            │  • stopRecording()       │
            │                          │
            │  Uses:                   │
            │  • getDisplayMedia()     │
            │  • getUserMedia()        │
            │  • MediaRecorder API     │
            └──────────────────────────┘
```

## Data Flow

### Recording Initialization
```
SelectionWindow (Area Mode)
    │
    ├── User draws selection
    │   └── setSelectedArea({ x, y, width, height })
    │
    └── Click "Start Recording"
        └── onStartRecording()
            └── Parent sets view to 'recording'

RecordingToolbar
    │
    ├── autoStart={true}
    │   └── useRecording.startRecording()
    │       ├── getDisplayMedia() → videoStream
    │       ├── getUserMedia() if mic enabled → audioStream
    │       ├── Combine streams → combinedStream
    │       └── new MediaRecorder(combinedStream)
    │           ├── recorder.ondataavailable → addRecordedChunk()
    │           └── recorder.start(1000) // 1-second chunks
    │
    └── Recording active
        └── Chunks accumulate in store
```

### Recording Completion
```
RecordingToolbar
    │
    └── User clicks "Finish"
        └── handleFinish()
            ├── mediaRecorder.stop()
            │   └── Triggers onstop event
            │       ├── Wait 200ms for final chunks
            │       ├── Get all chunks from store
            │       └── Create blob: new Blob(chunks, {type: 'video/webm'})
            │
            └── onFinish(blob)
                └── Parent handles blob
                    ├── Download
                    ├── Upload to server
                    └── Or process further
```

## Browser API Interactions

```
Component              Browser API              Result
─────────────────────────────────────────────────────────────
RecordingToolbar  →  getDisplayMedia()    →  Screen selection
                                              picker shown

useRecording      →  getUserMedia()       →  Microphone access
                     (audio: true)

useRecording      →  new MediaRecorder()  →  Recording instance
                     (stream, options)

MediaRecorder     →  ondataavailable      →  Blob chunks
                     event fires             every 1 second

MediaRecorder     →  onstop event         →  Recording complete,
                                             finalize blob
```

## Error Handling Flow

```
Try to start recording
    │
    ├─→ getDisplayMedia() fails
    │   └── User cancelled picker / No permission
    │       └── Show alert "Failed to start recording"
    │           └── Stay on current screen
    │
    ├─→ getUserMedia() fails (mic)
    │   └── Continue without audio
    │       └── Log warning
    │
    └─→ MediaRecorder constructor fails
        └── Try VP8 fallback
            ├─→ Success: Continue with VP8
            └─→ Fail: Show error, cannot record
```

## Component Lifecycle

### StartScreen
```
Mount → Render → Wait for user interaction → Unmount
```

### ControlBar
```
Mount → Render → User selects mode → Callback → Unmount
```

### SelectionWindow
```
Mount → Setup keyboard listeners
     → Render overlay
     → User interaction
        ├── Area: Draw selection → Click start
        └── Window/Display: Auto-trigger
     → Cleanup listeners → Unmount
```

### RecordingToolbar
```
Mount → Auto-start if enabled
     → Start timer interval
     → Recording active
     → User controls (pause/resume/restart)
     → Stop recording
     → Wait for chunks
     → Create blob
     → Callback with blob
     → Cleanup → Unmount
```

## Integration Points

Where these components connect to your app:

```
Your App
    │
    ├─→ Import components
    │   └── from './video-editor'
    │
    ├─→ Manage view state
    │   └── useState<'start' | 'control-bar' | ...>()
    │
    ├─→ Handle recording blob
    │   └── onFinish={(blob) => {
    │          // Your logic here
    │       }}
    │
    └─→ Wrap with theme
        └── <ThemeProvider theme={theme}>
```

## File Dependencies

```
StartScreen.tsx
├── styled-components
├── react
└── (no other dependencies)

ControlBar.tsx
├── styled-components
├── react
├── ../store (useRecordingStore)
└── ./Icons

SelectionWindow.tsx
├── styled-components
├── react
├── ../store (useRecordingStore)
└── ./Icons

RecordingToolbar.tsx
├── styled-components
├── react
├── ../store (useRecordingStore)
├── ../hooks/useRecording
└── ./Icons

useRecording.ts
└── ../store (useRecordingStore)

store/index.ts
└── zustand

theme/index.ts
└── (no dependencies)
```

// Components
export * from './components';

// Store
export { useRecordingStore, useEditorStore } from './store';
export type { MediaItem, TimelineClip, TimelineTrack, ZoomSegment, CursorPosition } from './store';

// Theme
export { theme } from './theme';
export type { Theme } from './theme';

// Hooks
export { useRecording } from './hooks/useRecording';

// Example
export { default as RecordingExample } from './RecordingExample';

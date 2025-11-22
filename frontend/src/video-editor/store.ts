import { create } from 'zustand';

// Recording State
export interface RecordingState {
  isRecording: boolean;
  isPaused: boolean;
  recordingTime: number;
  recordingMode: 'area' | 'window' | 'display' | null;
  selectedArea: {
    x: number;
    y: number;
    width: number;
    height: number;
  } | null;
  selectedSourceId: string | null;
  mediaStream: MediaStream | null;
  mediaRecorder: MediaRecorder | null;
  recordedChunks: Blob[];
  micEnabled: boolean;
  cameraEnabled: boolean;

  setRecordingMode: (mode: 'area' | 'window' | 'display' | null) => void;
  setSelectedArea: (area: RecordingState['selectedArea']) => void;
  setSelectedSourceId: (id: string | null) => void;
  setMediaStream: (stream: MediaStream | null) => void;
  setMediaRecorder: (recorder: MediaRecorder | null) => void;
  addRecordedChunk: (chunk: Blob) => void;
  clearRecordedChunks: () => void;
  setIsRecording: (isRecording: boolean) => void;
  setIsPaused: (isPaused: boolean) => void;
  setRecordingTime: (time: number) => void;
  toggleMic: () => void;
  toggleCamera: () => void;
  reset: () => void;
}

export const useRecordingStore = create<RecordingState>((set) => ({
  isRecording: false,
  isPaused: false,
  recordingTime: 0,
  recordingMode: null,
  selectedArea: null,
  selectedSourceId: null,
  mediaStream: null,
  mediaRecorder: null,
  recordedChunks: [],
  micEnabled: false,
  cameraEnabled: false,

  setRecordingMode: (mode) => set({ recordingMode: mode }),
  setSelectedArea: (area) => set({ selectedArea: area }),
  setSelectedSourceId: (id) => set({ selectedSourceId: id }),
  setMediaStream: (stream) => set({ mediaStream: stream }),
  setMediaRecorder: (recorder) => set({ mediaRecorder: recorder }),
  addRecordedChunk: (chunk) =>
    set((state) => ({
      recordedChunks: [...state.recordedChunks, chunk],
    })),
  clearRecordedChunks: () => set({ recordedChunks: [] }),
  setIsRecording: (isRecording) => set({ isRecording }),
  setIsPaused: (isPaused) => set({ isPaused }),
  setRecordingTime: (time) => set({ recordingTime: time }),
  toggleMic: () => set((state) => ({ micEnabled: !state.micEnabled })),
  toggleCamera: () => set((state) => ({ cameraEnabled: !state.cameraEnabled })),
  reset: () =>
    set({
      isRecording: false,
      isPaused: false,
      recordingTime: 0,
      recordingMode: null,
      selectedArea: null,
      selectedSourceId: null,
      mediaStream: null,
      mediaRecorder: null,
      recordedChunks: [],
    }),
}));

// Video Editor Types
export interface CursorPosition {
  x: number;
  y: number;
  timestamp: number; // milliseconds from start of recording
}

export interface MediaItem {
  id: string;
  name: string;
  type: 'video' | 'audio' | 'image';
  filePath: string; // Can be URL or blob URL in browser
  duration: number;
  thumbnail?: string;
  width?: number;
  height?: number;
  fileSize: number;
  cursorData?: CursorPosition[]; // Mouse tracking data for native recordings
}

export interface TimelineClip {
  id: string;
  mediaItemId: string;
  trackId: string;
  startTime: number; // Position on timeline in seconds
  duration: number;  // Duration in seconds
  trimStart: number; // Trim from start of source in seconds
  trimEnd: number;   // Trim from end of source in seconds
  volume: number;    // 0-1
  effects?: string[]; // Effect IDs
}

export interface TimelineTrack {
  id: string;
  type: 'video' | 'audio' | 'text';
  name: string;
  clips: TimelineClip[];
  locked: boolean;
  visible: boolean;
}

export interface ZoomSegment {
  id: string;
  startTime: number; // Position on timeline in seconds
  duration: number;  // Duration in seconds
  zoomLevel: number; // 1.0-2.0 (1.0 = no zoom, 2.0 = 2x zoom)
  mode: 'auto' | 'manual'; // auto follows cursor, manual is user-controlled
  targetX?: number; // Manual mode: target X position (0-1, relative to video width)
  targetY?: number; // Manual mode: target Y position (0-1, relative to video height)
}

interface HistoryState {
  tracks: TimelineTrack[];
  duration: number;
}

interface EditorState {
  // Media library
  mediaItems: MediaItem[];
  selectedMediaItemId: string | null;

  // Timeline
  tracks: TimelineTrack[];
  currentTime: number;
  zoom: number; // Pixels per second
  isPlaying: boolean;
  duration: number; // Total timeline duration

  // Zoom segments
  zoomSegments: ZoomSegment[];
  selectedZoomSegmentId: string | null;

  // Selection
  selectedClipIds: string[];
  selectedTrackId: string | null;

  // Export
  exportProgress: number;
  isExporting: boolean;

  // Undo/Redo
  history: HistoryState[];
  historyIndex: number;

  // Actions
  addMediaItem: (item: MediaItem) => void;
  removeMediaItem: (id: string) => void;
  setSelectedMediaItem: (id: string | null) => void;

  addTrack: (track: TimelineTrack) => void;
  removeTrack: (id: string) => void;
  updateTrack: (id: string, updates: Partial<TimelineTrack>) => void;

  addClip: (clip: TimelineClip) => void;
  removeClip: (id: string) => void;
  updateClip: (id: string, updates: Partial<TimelineClip>, skipHistory?: boolean) => void;
  splitClip: (clipId: string, splitTime: number) => void;
  pushToHistory: () => void;

  addZoomSegment: (segment: ZoomSegment) => void;
  removeZoomSegment: (id: string) => void;
  updateZoomSegment: (id: string, updates: Partial<ZoomSegment>) => void;
  setSelectedZoomSegment: (id: string | null) => void;

  setCurrentTime: (time: number) => void;
  setZoom: (zoom: number) => void;
  setIsPlaying: (isPlaying: boolean) => void;
  setDuration: (duration: number) => void;

  setSelectedClips: (ids: string[]) => void;
  setSelectedTrack: (id: string | null) => void;

  setExportProgress: (progress: number) => void;
  setIsExporting: (isExporting: boolean) => void;

  undo: () => void;
  redo: () => void;
  canUndo: () => boolean;
  canRedo: () => boolean;

  resetEditor: () => void;
}

// Helper to deep clone state for history
const cloneHistoryState = (state: EditorState): HistoryState => ({
  tracks: JSON.parse(JSON.stringify(state.tracks)),
  duration: state.duration,
});

// Helper to push current state to history
const pushHistory = (state: EditorState): Partial<EditorState> => {
  const currentState = cloneHistoryState(state);
  const newHistory = state.history.slice(0, state.historyIndex + 1);
  newHistory.push(currentState);

  // Limit history to 50 entries
  const limitedHistory = newHistory.length > 50 ? newHistory.slice(-50) : newHistory;

  return {
    history: limitedHistory,
    historyIndex: limitedHistory.length - 1,
  };
};

export const useEditorStore = create<EditorState>((set, get) => ({
  // Initial state
  mediaItems: [],
  selectedMediaItemId: null,
  tracks: [],
  currentTime: 0,
  zoom: 50, // 50 pixels per second
  isPlaying: false,
  duration: 0,
  zoomSegments: [],
  selectedZoomSegmentId: null,
  selectedClipIds: [],
  selectedTrackId: null,
  exportProgress: 0,
  isExporting: false,
  history: [{ tracks: [], duration: 0 }], // Initialize with empty state
  historyIndex: 0,

  // Media library actions
  addMediaItem: (item) =>
    set((state) => ({
      mediaItems: [...state.mediaItems, item],
    })),

  removeMediaItem: (id) =>
    set((state) => {
      // Also remove all clips using this media item
      const updatedTracks = state.tracks.map((track) => ({
        ...track,
        clips: track.clips.filter((clip) => clip.mediaItemId !== id),
      }));

      return {
        mediaItems: state.mediaItems.filter((item) => item.id !== id),
        selectedMediaItemId:
          state.selectedMediaItemId === id ? null : state.selectedMediaItemId,
        tracks: updatedTracks,
      };
    }),

  setSelectedMediaItem: (id) => set({ selectedMediaItemId: id }),

  // Track actions
  addTrack: (track) =>
    set((state) => {
      const newTracks = [...state.tracks, track];
      const newState = { ...state, tracks: newTracks };
      return {
        tracks: newTracks,
        ...pushHistory(newState),
      };
    }),

  removeTrack: (id) =>
    set((state) => {
      const newTracks = state.tracks.filter((track) => track.id !== id);
      const newSelectedTrackId = state.selectedTrackId === id ? null : state.selectedTrackId;
      const newState = { ...state, tracks: newTracks, selectedTrackId: newSelectedTrackId };
      return {
        tracks: newTracks,
        selectedTrackId: newSelectedTrackId,
        ...pushHistory(newState),
      };
    }),

  updateTrack: (id, updates) =>
    set((state) => {
      const newTracks = state.tracks.map((track) =>
        track.id === id ? { ...track, ...updates } : track
      );
      const newState = { ...state, tracks: newTracks };
      return {
        tracks: newTracks,
        ...pushHistory(newState),
      };
    }),

  // Clip actions
  addClip: (clip) =>
    set((state) => {
      const track = state.tracks.find((t) => t.id === clip.trackId);
      if (!track) return state;

      const updatedTracks = state.tracks.map((t) =>
        t.id === clip.trackId
          ? { ...t, clips: [...t.clips, clip] }
          : t
      );

      // Update duration if clip extends timeline
      const clipEnd = clip.startTime + clip.duration;
      const newDuration = Math.max(state.duration, clipEnd);

      const newState = { ...state, tracks: updatedTracks, duration: newDuration };
      return {
        tracks: updatedTracks,
        duration: newDuration,
        ...pushHistory(newState),
      };
    }),

  removeClip: (id) =>
    set((state) => {
      const newTracks = state.tracks.map((track) => ({
        ...track,
        clips: track.clips.filter((clip) => clip.id !== id),
      }));
      const newSelectedClipIds = state.selectedClipIds.filter((clipId) => clipId !== id);
      const newState = { ...state, tracks: newTracks, selectedClipIds: newSelectedClipIds };
      return {
        tracks: newTracks,
        selectedClipIds: newSelectedClipIds,
        ...pushHistory(newState),
      };
    }),

  updateClip: (id, updates, skipHistory = false) =>
    set((state) => {
      const updatedTracks = state.tracks.map((track) => ({
        ...track,
        clips: track.clips.map((clip) =>
          clip.id === id ? { ...clip, ...updates } : clip
        ),
      }));

      // Recalculate duration
      let maxDuration = 0;
      updatedTracks.forEach((track) => {
        track.clips.forEach((clip) => {
          const clipEnd = clip.startTime + clip.duration;
          maxDuration = Math.max(maxDuration, clipEnd);
        });
      });

      if (skipHistory) {
        return {
          tracks: updatedTracks,
          duration: maxDuration,
        };
      }

      const newState = { ...state, tracks: updatedTracks, duration: maxDuration };
      return {
        tracks: updatedTracks,
        duration: maxDuration,
        ...pushHistory(newState),
      };
    }),

  splitClip: (clipId, splitTime) =>
    set((state) => {
      let splitTrack: TimelineTrack | null = null;
      let splitClip: TimelineClip | null = null;

      // Find the clip to split
      for (const track of state.tracks) {
        const clip = track.clips.find((c: TimelineClip) => c.id === clipId);
        if (clip) {
          splitTrack = track;
          splitClip = clip;
          break;
        }
      }

      if (!splitClip || !splitTrack) return state;

      // Calculate split position relative to clip start
      const relativeTime = splitTime - splitClip.startTime;
      if (relativeTime <= 0 || relativeTime >= splitClip.duration) return state;

      // Create two new clips
      const clip1: TimelineClip = {
        ...splitClip,
        id: `${splitClip.id}-1`,
        duration: relativeTime,
        trimEnd: splitClip.trimEnd + (splitClip.duration - relativeTime),
      };

      const clip2: TimelineClip = {
        ...splitClip,
        id: `${splitClip.id}-2`,
        startTime: splitTime,
        duration: splitClip.duration - relativeTime,
        trimStart: splitClip.trimStart + relativeTime,
      };

      // Update tracks with split clips
      const updatedTracks = state.tracks.map((track) =>
        track.id === splitTrack!.id
          ? {
              ...track,
              clips: track.clips
                .filter((c: TimelineClip) => c.id !== clipId)
                .concat([clip1, clip2])
                .sort((a: TimelineClip, b: TimelineClip) => a.startTime - b.startTime),
            }
          : track
      );

      const newSelectedClipIds = [clip1.id, clip2.id];
      const newState = { ...state, tracks: updatedTracks, selectedClipIds: newSelectedClipIds };
      return {
        tracks: updatedTracks,
        selectedClipIds: newSelectedClipIds,
        ...pushHistory(newState),
      };
    }),

  // Zoom segment actions
  addZoomSegment: (segment) =>
    set((state) => ({
      zoomSegments: [...state.zoomSegments, segment],
      selectedZoomSegmentId: segment.id,
    })),

  removeZoomSegment: (id) =>
    set((state) => ({
      zoomSegments: state.zoomSegments.filter((segment) => segment.id !== id),
      selectedZoomSegmentId: state.selectedZoomSegmentId === id ? null : state.selectedZoomSegmentId,
    })),

  updateZoomSegment: (id, updates) =>
    set((state) => ({
      zoomSegments: state.zoomSegments.map((segment) =>
        segment.id === id ? { ...segment, ...updates } : segment
      ),
    })),

  setSelectedZoomSegment: (id) => set({ selectedZoomSegmentId: id }),

  // Playback actions
  setCurrentTime: (time) => set({ currentTime: time }),
  setZoom: (zoom) => set({ zoom }),
  setIsPlaying: (isPlaying) => set({ isPlaying }),
  setDuration: (duration) => set({ duration }),

  // Selection actions
  setSelectedClips: (ids) => set({ selectedClipIds: ids }),
  setSelectedTrack: (id) => set({ selectedTrackId: id }),

  // Export actions
  setExportProgress: (progress) => set({ exportProgress: progress }),
  setIsExporting: (isExporting) => set({ isExporting }),

  // Undo/Redo actions
  pushToHistory: () =>
    set((state) => pushHistory(state)),

  undo: () =>
    set((state) => {
      if (state.historyIndex <= 0) return state; // Can't undo from initial state

      const newIndex = state.historyIndex - 1;
      const previousState = state.history[newIndex];
      return {
        tracks: previousState.tracks,
        duration: previousState.duration,
        historyIndex: newIndex,
        selectedClipIds: [], // Clear selection on undo
      };
    }),

  redo: () =>
    set((state) => {
      if (state.historyIndex >= state.history.length - 1) return state;

      const newIndex = state.historyIndex + 1;
      const nextState = state.history[newIndex];
      return {
        tracks: nextState.tracks,
        duration: nextState.duration,
        historyIndex: newIndex,
        selectedClipIds: [], // Clear selection on redo
      };
    }),

  canUndo: () => {
    const state = get();
    return state.historyIndex > 0;
  },

  canRedo: () => {
    const state = get();
    return state.historyIndex < state.history.length - 1;
  },

  // Reset
  resetEditor: () =>
    set({
      mediaItems: [],
      selectedMediaItemId: null,
      tracks: [],
      currentTime: 0,
      zoom: 50,
      isPlaying: false,
      duration: 0,
      zoomSegments: [],
      selectedZoomSegmentId: null,
      selectedClipIds: [],
      selectedTrackId: null,
      exportProgress: 0,
      isExporting: false,
      history: [{ tracks: [], duration: 0 }],
      historyIndex: 0,
    }),
}));

import { contextBridge, ipcRenderer } from 'electron';

export interface DesktopCapturerSource {
  id: string;
  name: string;
  thumbnail: string;
  appIcon?: string;
  bounds?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}

export interface Display {
  id: number;
  bounds: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  workArea: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  size: {
    width: number;
    height: number;
  };
  scaleFactor: number;
  rotation: number;
  internal: boolean;
}

export interface HitTestWindow {
  windowNumber: number;
  ownerName: string;
  name: string;
  pid: number;
  bounds: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}

contextBridge.exposeInMainWorld('electronAPI', {
  getSources: (): Promise<DesktopCapturerSource[]> =>
    ipcRenderer.invoke('get-sources'),

  getDisplays: (): Promise<Display[]> =>
    ipcRenderer.invoke('get-displays'),

  hitTestWindow: (x: number, y: number): Promise<HitTestWindow | {}> =>
    ipcRenderer.invoke('hit-test-window', x, y),

  openSelection: (mode: 'area' | 'window' | 'display'): void =>
    ipcRenderer.send('open-selection', mode),

  closeSelection: (): void =>
    ipcRenderer.send('close-selection'),

  startRecording: (config?: { selectedSourceId?: string | null; selectedArea?: { x: number; y: number; width: number; height: number } | null }): void =>
    ipcRenderer.send('start-recording', config),

  stopRecording: (): void =>
    ipcRenderer.send('stop-recording'),

  saveRecording: (videoData: Buffer): Promise<{ success: boolean; filePath?: string; canceled?: boolean; error?: string }> =>
    ipcRenderer.invoke('save-recording', videoData),

  checkFFmpeg: (): Promise<boolean> =>
    ipcRenderer.invoke('check-ffmpeg'),

  getRecordingConfig: (): Promise<{ selectedSourceId?: string | null; selectedArea?: { x: number; y: number; width: number; height: number } | null } | null> =>
    ipcRenderer.invoke('get-recording-config'),

  // Editor APIs
  openEditor: (videoData?: Uint8Array): void =>
    ipcRenderer.send('open-editor', videoData),

  getPendingRecording: (): Promise<{
    filePath: string;
    name: string;
    type: string;
    duration: number;
    width?: number;
    height?: number;
    fileSize: number;
    cursorData?: Array<{ x: number; y: number; timestamp: number }>;
  } | null> =>
    ipcRenderer.invoke('get-pending-recording'),

  importMediaFiles: (): Promise<{ success: boolean; files?: Array<{ filePath: string; name: string; type: string; duration: number; width?: number; height?: number; fileSize: number }>; canceled?: boolean; error?: string }> =>
    ipcRenderer.invoke('import-media-files'),

  getVideoMetadata: (filePath: string): Promise<{ type: 'video' | 'audio' | 'image'; duration: number; width?: number; height?: number }> =>
    ipcRenderer.invoke('get-video-metadata', filePath),

  generateThumbnail: (filePath: string, timestamp?: number): Promise<string> =>
    ipcRenderer.invoke('generate-thumbnail', filePath, timestamp),

  exportVideo: (options: {
    outputPath: string;
    clips: Array<{ filePath: string; startTime: number; duration: number; trimStart: number; trimEnd: number }>;
    resolution?: { width: number; height: number };
    format?: string;
    quality?: 'low' | 'medium' | 'high' | 'ultra';
  }): Promise<{ success: boolean; outputPath?: string; error?: string }> =>
    ipcRenderer.invoke('export-video', options),

  showSaveDialog: (options: {
    title?: string;
    defaultPath?: string;
    filters?: Array<{ name: string; extensions: string[] }>;
  }): Promise<{ filePath?: string; canceled: boolean }> =>
    ipcRenderer.invoke('show-save-dialog', options),

  onExportProgress: (callback: (progress: number) => void): void => {
    ipcRenderer.on('export-progress', (_event, progress) => callback(progress));
  },
});

declare global {
  interface Window {
    electronAPI: {
      getSources: () => Promise<DesktopCapturerSource[]>;
      getDisplays: () => Promise<Display[]>;
      hitTestWindow: (x: number, y: number) => Promise<HitTestWindow | {}>;
      openSelection: (mode: 'area' | 'window' | 'display') => void;
      closeSelection: () => void;
      startRecording: (config?: { selectedSourceId?: string | null; selectedArea?: { x: number; y: number; width: number; height: number } | null }) => void;
      stopRecording: () => void;
      saveRecording: (videoData: Buffer) => Promise<{ success: boolean; filePath?: string; canceled?: boolean; error?: string }>;
      checkFFmpeg: () => Promise<boolean>;
      getRecordingConfig: () => Promise<{ selectedSourceId?: string | null; selectedArea?: { x: number; y: number; width: number; height: number } | null } | null>;
      openEditor: (videoData?: Uint8Array) => void;
      getPendingRecording: () => Promise<{
        filePath: string;
        name: string;
        type: string;
        duration: number;
        width?: number;
        height?: number;
        fileSize: number;
        cursorData?: Array<{ x: number; y: number; timestamp: number }>;
      } | null>;
      importMediaFiles: () => Promise<{ success: boolean; files?: Array<{ filePath: string; name: string; type: string; duration: number; width?: number; height?: number; fileSize: number }>; canceled?: boolean; error?: string }>;
      getVideoMetadata: (filePath: string) => Promise<{ type: 'video' | 'audio' | 'image'; duration: number; width?: number; height?: number }>;
      generateThumbnail: (filePath: string, timestamp?: number) => Promise<string>;
      exportVideo: (options: {
        outputPath: string;
        clips: Array<{ filePath: string; startTime: number; duration: number; trimStart: number; trimEnd: number }>;
        resolution?: { width: number; height: number };
        format?: string;
        quality?: 'low' | 'medium' | 'high' | 'ultra';
      }) => Promise<{ success: boolean; outputPath?: string; error?: string }>;
      showSaveDialog: (options: {
        title?: string;
        defaultPath?: string;
        filters?: Array<{ name: string; extensions: string[] }>;
      }) => Promise<{ filePath?: string; canceled: boolean }>;
      onExportProgress: (callback: (progress: number) => void) => void;
    };
  }
}

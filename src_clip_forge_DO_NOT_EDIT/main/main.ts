import { app, BrowserWindow, ipcMain, desktopCapturer, screen, dialog, protocol, Tray, nativeImage, Menu } from 'electron';
import path from 'path';
import Store from 'electron-store';
import fs from 'fs/promises';
import ffmpeg from 'fluent-ffmpeg';

// Set up FFmpeg and FFprobe paths
// In packaged app, they're in Resources folder; in dev, they're in node_modules
const setupFFmpeg = () => {
  try {
    if (app.isPackaged) {
      // In production, FFmpeg binaries are in Resources/@ffmpeg-installer
      const resourcesPath = process.resourcesPath;
      const platform = process.platform + '-' + process.arch;

      const ffmpegPath = path.join(resourcesPath, '@ffmpeg-installer', platform, process.platform === 'win32' ? 'ffmpeg.exe' : 'ffmpeg');
      const ffprobePath = path.join(resourcesPath, '@ffprobe-installer', platform, process.platform === 'win32' ? 'ffprobe.exe' : 'ffprobe');

      console.log('Packaged app - FFmpeg path:', ffmpegPath);
      console.log('Packaged app - FFprobe path:', ffprobePath);

      ffmpeg.setFfmpegPath(ffmpegPath);
      ffmpeg.setFfprobePath(ffprobePath);
    } else {
      // In development, use the npm packages
      const ffmpegInstaller = require('@ffmpeg-installer/ffmpeg');
      const ffprobeInstaller = require('@ffprobe-installer/ffprobe');

      console.log('Development - FFmpeg path:', ffmpegInstaller.path);
      console.log('Development - FFprobe path:', ffprobeInstaller.path);

      ffmpeg.setFfmpegPath(ffmpegInstaller.path);
      ffmpeg.setFfprobePath(ffprobeInstaller.path);
    }
  } catch (error) {
    console.error('Error setting up FFmpeg/FFprobe:', error);
  }
};

// Call setup immediately
setupFFmpeg();

// Load native addon with proper path resolution
// Try multiple paths to handle both dev and production builds
interface WindowHelper {
  getOnScreenWindows: () => Array<{
    windowNumber: number;
    ownerName: string;
    name: string;
    pid: number;
    bounds: { x: number; y: number; width: number; height: number };
  }>;
  getWindowAtPoint: (x: number, y: number) => {
    windowNumber?: number;
    ownerName?: string;
    name?: string;
    pid?: number;
    bounds?: { x: number; y: number; width: number; height: number };
  };
}

interface MouseTracker {
  startTracking: () => boolean;
  stopTracking: () => void;
  getPositions: () => Array<{
    x: number;
    y: number;
    timestamp: number;
  }>;
  clearPositions: () => void;
  isTracking: () => boolean;
}

let windowHelper: WindowHelper | undefined;
let mouseTracker: MouseTracker | undefined;

// Determine the base path for native modules
const getBasePath = () => {
  if (app.isPackaged) {
    // In production, native modules are in Resources directory
    return process.resourcesPath;
  } else {
    // In development, use project root
    return process.cwd();
  }
};

const possiblePaths = [
  // Development path (from project root) or packaged path (from Resources)
  path.join(getBasePath(), 'native', 'window-helper'),
  // Unpacked from asar
  path.join(__dirname, '..', '..', 'native', 'window-helper'),
  // Alternative unpacked location
  path.join(__dirname, '..', '..', '..', 'Resources', 'native', 'window-helper'),
];

for (const addonPath of possiblePaths) {
  try {
    windowHelper = require(addonPath);
    console.log('Successfully loaded window helper from:', addonPath);
    break;
  } catch (e) {
    console.log('Failed to load from:', addonPath);
  }
}

if (!windowHelper) {
  throw new Error('Could not load window_helper native addon from any path. Tried: ' + possiblePaths.join(', '));
}

// Load mouse tracker addon
const mouseTrackerPaths = [
  path.join(getBasePath(), 'native', 'mouse-tracker'),
  path.join(__dirname, '..', '..', 'native', 'mouse-tracker'),
  path.join(__dirname, '..', '..', '..', 'Resources', 'native', 'mouse-tracker'),
];

for (const addonPath of mouseTrackerPaths) {
  try {
    mouseTracker = require(addonPath);
    console.log('Successfully loaded mouse tracker from:', addonPath);
    break;
  } catch (e) {
    console.log('Failed to load mouse tracker from:', addonPath);
  }
}

if (!mouseTracker) {
  console.warn('Could not load mouse_tracker native addon. Cursor tracking will not be available.');
}

// In development mode, these are provided by Vite
// In production, they're provided by Electron Forge
declare const MAIN_WINDOW_VITE_DEV_SERVER_URL: string;
declare const MAIN_WINDOW_VITE_NAME: string;

// Initialize store for future use
new Store();

let controlBar: BrowserWindow | null = null;
let selectionWindow: BrowserWindow | null = null;
let recordingToolbar: BrowserWindow | null = null;
let editorWindow: BrowserWindow | null = null;
let recordingConfig: { selectedSourceId?: string | null; selectedArea?: { x: number; y: number; width: number; height: number } | null } | null = null;
let pendingRecordingData: Uint8Array | null = null;
let pendingCursorData: Array<{ x: number; y: number; timestamp: number }> | null = null;
let tray: Tray | null = null;

const createTray = (): void => {
  // Create a simple 16x16 circle icon for the tray
  // Using a simple shape that will definitely be visible
  const canvas = `
  <svg width="16" height="16" xmlns="http://www.w3.org/2000/svg">
    <circle cx="8" cy="8" r="6" fill="black" />
    <circle cx="8" cy="8" r="3" fill="red" />
  </svg>`;

  const iconData = 'data:image/svg+xml;base64,' + Buffer.from(canvas).toString('base64');
  const icon = nativeImage.createFromDataURL(iconData);
  icon.setTemplateImage(true); // This makes it adapt to light/dark menu bar

  tray = new Tray(icon);
  tray.setToolTip('Clip Forge - Screen Recording');

  console.log('Tray created successfully');

  // Create context menu for the tray
  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Show Clip Forge',
      click: () => {
        if (controlBar) {
          controlBar.show();
          controlBar.focus();
        } else {
          createControlBar();
        }
      }
    },
    { type: 'separator' },
    {
      label: 'Quit',
      click: () => {
        app.quit();
      }
    }
  ]);

  tray.setContextMenu(contextMenu);

  // Show window when tray icon is clicked
  tray.on('click', () => {
    if (controlBar) {
      if (controlBar.isVisible()) {
        controlBar.focus();
      } else {
        controlBar.show();
        controlBar.focus();
      }
    } else {
      createControlBar();
    }
  });
};

const createControlBar = (startWithHash?: string): void => {
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width, height } = primaryDisplay.workAreaSize;

  // Default dimensions for start screen, can be modified for control bar
  const windowWidth = startWithHash === '#control-bar' ? 600 : 400;
  const windowHeight = startWithHash === '#control-bar' ? 80 : 140;

  // Position based on mode
  const xPos = Math.floor((width - windowWidth) / 2);
  const yPos = startWithHash === '#control-bar' ? 20 : Math.floor((height - windowHeight) / 2);

  controlBar = new BrowserWindow({
    width: windowWidth,
    height: windowHeight,
    x: xPos,
    y: yPos,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    resizable: false,
    minimizable: false,
    maximizable: false,
    skipTaskbar: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  // Load the index.html of the app.
  if (MAIN_WINDOW_VITE_DEV_SERVER_URL) {
    const url = startWithHash ? `${MAIN_WINDOW_VITE_DEV_SERVER_URL}${startWithHash}` : MAIN_WINDOW_VITE_DEV_SERVER_URL;
    controlBar.loadURL(url);
  } else {
    controlBar.loadFile(path.join(__dirname, `../renderer/${MAIN_WINDOW_VITE_NAME}/index.html`), {
      hash: startWithHash?.replace('#', '') || '',
    });
  }

  controlBar.setAlwaysOnTop(true, 'screen-saver');
  controlBar.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true });

  // Open DevTools in development
  if (MAIN_WINDOW_VITE_DEV_SERVER_URL) {
    controlBar.webContents.openDevTools({ mode: 'detach' });
  }

  // Listen for hash changes to resize/reposition window
  controlBar.webContents.on('did-navigate-in-page', (_event, url) => {
    const hash = new URL(url).hash;
    if (hash === '#editor') {
      // Close control bar and open editor window
      controlBar?.hide();
      createEditorWindow();
    } else if (hash === '#control-bar') {
      controlBar?.setBounds({
        width: 600,
        height: 80,
        x: Math.floor((width - 600) / 2),
        y: 20,
      });
    } else if (hash === '' || hash === '#start-screen') {
      controlBar?.setBounds({
        width: 400,
        height: 140,
        x: Math.floor((width - 400) / 2),
        y: Math.floor((height - 140) / 2),
      });
    }
  });
};

const createSelectionWindow = (mode: 'area' | 'window' | 'display'): void => {
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width, height, x, y } = primaryDisplay.bounds;

  if (selectionWindow) {
    selectionWindow.close();
  }

  selectionWindow = new BrowserWindow({
    width,
    height,
    x,
    y,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    resizable: false,
    minimizable: false,
    maximizable: false,
    skipTaskbar: true,
    hasShadow: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  if (MAIN_WINDOW_VITE_DEV_SERVER_URL) {
    selectionWindow.loadURL(`${MAIN_WINDOW_VITE_DEV_SERVER_URL}#selection/${mode}`);
  } else {
    selectionWindow.loadFile(path.join(__dirname, `../renderer/${MAIN_WINDOW_VITE_NAME}/index.html`), {
      hash: `selection/${mode}`,
    });
  }

  selectionWindow.setAlwaysOnTop(true, 'screen-saver');

  // Open DevTools in development
  if (MAIN_WINDOW_VITE_DEV_SERVER_URL) {
    selectionWindow.webContents.openDevTools({ mode: 'detach' });
  }

  selectionWindow.on('closed', () => {
    selectionWindow = null;
  });
};

const createRecordingToolbar = (): void => {
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width, height } = primaryDisplay.workAreaSize;

  recordingToolbar = new BrowserWindow({
    width: 380,
    height: 60,
    x: Math.floor((width - 380) / 2),
    y: height - 100,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    resizable: false,
    minimizable: false,
    maximizable: false,
    skipTaskbar: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  if (MAIN_WINDOW_VITE_DEV_SERVER_URL) {
    recordingToolbar.loadURL(`${MAIN_WINDOW_VITE_DEV_SERVER_URL}#recording-toolbar`);
  } else {
    recordingToolbar.loadFile(path.join(__dirname, `../renderer/${MAIN_WINDOW_VITE_NAME}/index.html`), {
      hash: 'recording-toolbar',
    });
  }

  recordingToolbar.setAlwaysOnTop(true, 'screen-saver');
  recordingToolbar.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true });

  // Open DevTools in development
  if (MAIN_WINDOW_VITE_DEV_SERVER_URL) {
    recordingToolbar.webContents.openDevTools({ mode: 'detach' });
  }
};

const createEditorWindow = (): void => {
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width, height } = primaryDisplay.workAreaSize;

  if (editorWindow) {
    editorWindow.focus();
    return;
  }

  editorWindow = new BrowserWindow({
    width: Math.floor(width * 0.9),
    height: Math.floor(height * 0.9),
    minWidth: 1200,
    minHeight: 700,
    frame: true,
    backgroundColor: '#0a0a0a',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  if (MAIN_WINDOW_VITE_DEV_SERVER_URL) {
    editorWindow.loadURL(`${MAIN_WINDOW_VITE_DEV_SERVER_URL}#editor`);
  } else {
    editorWindow.loadFile(path.join(__dirname, `../renderer/${MAIN_WINDOW_VITE_NAME}/index.html`), {
      hash: 'editor',
    });
  }

  // Open DevTools in development
  if (MAIN_WINDOW_VITE_DEV_SERVER_URL) {
    editorWindow.webContents.openDevTools({ mode: 'detach' });
  }

  editorWindow.on('closed', () => {
    editorWindow = null;
    pendingRecordingData = null;
  });
};

// Register custom protocol before app is ready
protocol.registerSchemesAsPrivileged([
  {
    scheme: 'media-file',
    privileges: {
      bypassCSP: true,
      supportFetchAPI: true,
      stream: true,
      corsEnabled: true,
    },
  },
]);

// App lifecycle
app.on('ready', () => {
  // Register custom protocol for local file access
  protocol.registerFileProtocol('media-file', (request, callback) => {
    const url = request.url.replace('media-file://', '');
    try {
      return callback(decodeURIComponent(url));
    } catch (error) {
      console.error('Failed to load media file:', error);
      return callback({ statusCode: 404 });
    }
  });

  // Create application menu (this makes the app name appear in menu bar)
  const template: any[] = [
    {
      label: app.name,
      submenu: [
        { role: 'about' },
        { type: 'separator' },
        { role: 'hide' },
        { role: 'hideOthers' },
        { role: 'unhide' },
        { type: 'separator' },
        { role: 'quit' }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);

  // Create tray icon - MUST be after ready event
  createTray();

  // Show dock icon (since windows use skipTaskbar)
  if (process.platform === 'darwin') {
    // Keep dock icon visible to ensure tray icon persists
    app.dock.show().catch(err => console.error('Failed to show dock:', err));
  }

  createControlBar();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createControlBar();
  }
});

// IPC Handlers
ipcMain.handle('get-sources', async () => {
  // Get real window bounds from CoreGraphics
  const realWindows = windowHelper.getOnScreenWindows();

  // Get thumbnails from desktopCapturer (for visual preview)
  const sources = await desktopCapturer.getSources({
    types: ['window', 'screen'],
    thumbnailSize: { width: 150, height: 150 },
    fetchWindowIcons: true,
  });

  // Map real windows with thumbnails from desktopCapturer
  const windowsWithBoundsAndThumbnails = realWindows.map((realWindow) => {
    // Try to find matching source by name
    const matchingSource = sources.find(s => {
      // desktopCapturer IDs are like "window:123:0" so we extract the window number
      const sourceWindowId = s.id.split(':')[1];
      return sourceWindowId === String(realWindow.windowNumber) || s.name === realWindow.name;
    });

    return {
      id: `window:${realWindow.windowNumber}:0`,
      name: realWindow.name || realWindow.ownerName,
      thumbnail: matchingSource?.thumbnail?.toDataURL?.() || null,
      appIcon: matchingSource?.appIcon?.toDataURL?.() || null,
      bounds: realWindow.bounds,
      ownerName: realWindow.ownerName,
      windowNumber: realWindow.windowNumber,
      pid: realWindow.pid,
    };
  });

  // Add screens (displays) with their real bounds
  const screens = sources.filter(s => s.id.startsWith('screen'));

  return [...windowsWithBoundsAndThumbnails, ...screens];
});

ipcMain.handle('get-displays', async () => {
  const displays = screen.getAllDisplays();
  return displays;
});

ipcMain.handle('hit-test-window', async (_event, x: number, y: number) => {
  const window = windowHelper.getWindowAtPoint(x, y);
  return window;
});

ipcMain.on('open-selection', (_event, mode: 'area' | 'window' | 'display') => {
  createSelectionWindow(mode);
});

ipcMain.on('close-selection', () => {
  if (selectionWindow) {
    selectionWindow.close();
    selectionWindow = null;
  }
});

ipcMain.on('start-recording', (_event, config?: { selectedSourceId?: string | null; selectedArea?: { x: number; y: number; width: number; height: number } | null }) => {
  // Store the recording config so RecordingToolbar can retrieve it
  recordingConfig = config || null;
  console.log('Main: Received start-recording with config:', recordingConfig);

  // Start mouse tracking if available
  if (mouseTracker) {
    try {
      const success = mouseTracker.startTracking();
      if (success) {
        console.log('Mouse tracking started successfully');
      } else {
        console.warn('Failed to start mouse tracking - may need accessibility permissions');
      }
    } catch (error) {
      console.error('Error starting mouse tracking:', error);
    }
  }

  // Ensure tray icon persists during recording
  if (!tray || tray.isDestroyed()) {
    console.log('Recreating tray icon for recording');
    createTray();
  }

  // Keep dock icon visible to maintain tray icon on macOS
  if (process.platform === 'darwin') {
    app.dock.show().catch(err => console.error('Failed to show dock during recording:', err));
  }

  if (controlBar) {
    controlBar.hide();
  }
  if (selectionWindow) {
    selectionWindow.close();
    selectionWindow = null;
  }
  createRecordingToolbar();
});

ipcMain.on('stop-recording', () => {
  if (recordingToolbar) {
    recordingToolbar.close();
    recordingToolbar = null;
  }
  // Clear the recording config
  recordingConfig = null;
  if (controlBar) {
    controlBar.show();
  }
});

ipcMain.handle('get-recording-config', async () => {
  console.log('Main: RecordingToolbar requesting config, returning:', recordingConfig);
  return recordingConfig;
});

ipcMain.handle('save-recording', async (_event, videoData: Buffer) => {
  const { filePath, canceled } = await dialog.showSaveDialog({
    title: 'Save Recording',
    defaultPath: `recording-${Date.now()}.mp4`,
    filters: [{ name: 'Video', extensions: ['mp4'] }],
  });

  if (canceled || !filePath) {
    return { success: false, canceled: true };
  }

  try {
    const fs = require('fs').promises;
    await fs.writeFile(filePath, videoData);
    return { success: true, filePath };
  } catch (error) {
    console.error('Error saving file:', error);
    return { success: false, error: String(error) };
  }
});

ipcMain.handle('check-ffmpeg', async () => {
  return new Promise((resolve) => {
    const { exec } = require('child_process');
    exec('ffmpeg -version', (error: Error | null) => {
      resolve(!error);
    });
  });
});

// Editor IPC Handlers
ipcMain.on('open-editor', (_event, videoData?: Uint8Array) => {
  if (videoData) {
    pendingRecordingData = videoData;
  }

  // Stop mouse tracking and capture data
  if (mouseTracker && mouseTracker.isTracking()) {
    try {
      const positions = mouseTracker.getPositions();
      pendingCursorData = positions;
      mouseTracker.stopTracking();
      console.log(`Captured ${positions.length} cursor positions`);
    } catch (error) {
      console.error('Error capturing cursor data:', error);
      pendingCursorData = null;
    }
  }

  // Ensure tray icon persists when opening editor
  if (!tray || tray.isDestroyed()) {
    console.log('Recreating tray icon for editor');
    createTray();
  }

  if (recordingToolbar) {
    recordingToolbar.close();
    recordingToolbar = null;
  }

  if (controlBar) {
    controlBar.hide();
  }

  createEditorWindow();
});

ipcMain.handle('get-pending-recording', async () => {
  if (!pendingRecordingData) {
    console.log('No pending recording data');
    return null;
  }

  try {
    console.log('Processing pending recording, data size:', pendingRecordingData.length, 'bytes');
    // Save to a temporary file
    const tempDir = app.getPath('temp');
    const timestamp = Date.now();
    const tempWebmPath = path.join(tempDir, `clip-forge-recording-${timestamp}.webm`);
    const tempMp4Path = path.join(tempDir, `clip-forge-recording-${timestamp}.mp4`);

    console.log('Temp directory:', tempDir);
    console.log('Saving recording to:', tempWebmPath);
    await fs.writeFile(tempWebmPath, pendingRecordingData);

    // Verify file was written
    const webmStats = await fs.stat(tempWebmPath);
    console.log('WebM file created, size:', webmStats.size, 'bytes');

    if (webmStats.size === 0) {
      throw new Error('Recorded file is empty');
    }

    // Convert webm to mp4 for better compatibility
    console.log('Starting FFmpeg conversion...');
    await new Promise<void>((resolve, reject) => {
      ffmpeg(tempWebmPath)
        .outputOptions([
          '-c:v libx264',  // H.264 codec
          '-preset ultrafast',   // Fast encoding for temp conversion
          '-crf 18',        // High quality
          '-c:a aac',       // AAC audio codec
          '-movflags +faststart', // Enable streaming
          '-pix_fmt yuv420p', // Ensure compatibility
        ])
        .output(tempMp4Path)
        .on('start', (commandLine) => {
          console.log('FFmpeg command:', commandLine);
        })
        .on('progress', (progress) => {
          console.log('FFmpeg progress:', progress.percent, '%');
        })
        .on('end', async () => {
          console.log('FFmpeg conversion complete');
          // Delete the original webm file after conversion completes
          try {
            await fs.unlink(tempWebmPath);
            console.log('Deleted temp WebM file');
          } catch (err) {
            console.warn('Failed to delete temp webm:', err);
          }
          resolve();
        })
        .on('error', (error, stdout, stderr) => {
          console.error('FFmpeg conversion error:', error);
          console.error('FFmpeg stdout:', stdout);
          console.error('FFmpeg stderr:', stderr);
          reject(error);
        })
        .run();
    });

    // Verify MP4 was created
    const mp4Stats = await fs.stat(tempMp4Path);
    console.log('MP4 file created, size:', mp4Stats.size, 'bytes');

    // Get metadata from the mp4 file
    const metadata = await getMediaMetadata(tempMp4Path);
    console.log('Video metadata:', metadata);

    // Clear pending data
    const cursorData = pendingCursorData;
    pendingRecordingData = null;
    pendingCursorData = null;

    return {
      filePath: tempMp4Path,
      name: `Recording ${new Date().toLocaleString()}`,
      type: metadata.type,
      duration: metadata.duration || 0,
      width: metadata.width,
      height: metadata.height,
      fileSize: mp4Stats.size,
      cursorData: cursorData || undefined,
    };
  } catch (error) {
    console.error('Error processing pending recording:', error);
    pendingRecordingData = null;
    pendingCursorData = null;
    return null;
  }
});

ipcMain.handle('import-media-files', async () => {
  const { filePaths, canceled } = await dialog.showOpenDialog({
    title: 'Import Media',
    properties: ['openFile', 'multiSelections'],
    filters: [
      { name: 'Media Files', extensions: ['mp4', 'mov', 'avi', 'mkv', 'webm', 'mp3', 'wav', 'aac', 'jpg', 'jpeg', 'png', 'gif'] },
      { name: 'Video', extensions: ['mp4', 'mov', 'avi', 'mkv', 'webm'] },
      { name: 'Audio', extensions: ['mp3', 'wav', 'aac', 'ogg', 'm4a'] },
      { name: 'Image', extensions: ['jpg', 'jpeg', 'png', 'gif', 'webp'] },
    ],
  });

  if (canceled || !filePaths.length) {
    return { success: false, canceled: true };
  }

  try {
    console.log('Importing media files:', filePaths);
    const mediaFiles = await Promise.all(
      filePaths.map(async (filePath) => {
        console.log('Processing file:', filePath);
        const stats = await fs.stat(filePath);
        console.log('File stats:', { size: stats.size, path: filePath });
        const metadata = await getMediaMetadata(filePath);
        console.log('File metadata:', metadata);

        return {
          filePath,
          name: path.basename(filePath),
          type: metadata.type,
          duration: metadata.duration,
          width: metadata.width,
          height: metadata.height,
          fileSize: stats.size,
        };
      })
    );

    console.log('Successfully imported', mediaFiles.length, 'files');
    return { success: true, files: mediaFiles };
  } catch (error) {
    console.error('Error importing files:', error);
    console.error('Error stack:', error instanceof Error ? error.stack : 'No stack trace');
    return { success: false, error: String(error) };
  }
});

ipcMain.handle('get-video-metadata', async (_event, filePath: string) => {
  return getMediaMetadata(filePath);
});

ipcMain.handle('generate-thumbnail', async (_event, filePath: string, timestamp: number = 0) => {
  return new Promise(async (resolve, reject) => {
    try {
      console.log('Generating thumbnail for:', filePath, 'at timestamp:', timestamp);

      // Verify the file exists and is accessible
      const stats = await fs.stat(filePath);
      console.log('File exists, size:', stats.size, 'bytes');

      // Wait a moment to ensure file handle is released
      await new Promise(resolve => setTimeout(resolve, 100));

      const tempPath = path.join(app.getPath('temp'), `thumb-${Date.now()}.jpg`);
      console.log('Temp thumbnail path:', tempPath);

      ffmpeg(filePath)
        .screenshots({
          timestamps: [timestamp],
          filename: path.basename(tempPath),
          folder: path.dirname(tempPath),
          size: '150x?',
        })
        .on('start', (commandLine) => {
          console.log('Thumbnail FFmpeg command:', commandLine);
        })
        .on('end', async () => {
          console.log('Thumbnail generated successfully');
          try {
            const data = await fs.readFile(tempPath);
            console.log('Thumbnail file read, size:', data.length, 'bytes');
            // Clean up temp file
            try {
              await fs.unlink(tempPath);
              console.log('Temp thumbnail deleted');
            } catch (unlinkError) {
              console.warn('Failed to delete temp thumbnail:', unlinkError);
            }
            resolve(`data:image/jpeg;base64,${data.toString('base64')}`);
          } catch (error) {
            console.error('Failed to read thumbnail file:', error);
            reject(error);
          }
        })
        .on('error', (error, stdout, stderr) => {
          console.error('Thumbnail generation error:', error);
          console.error('FFmpeg stdout:', stdout);
          console.error('FFmpeg stderr:', stderr);
          reject(error);
        });
    } catch (error) {
      console.error('Thumbnail generation failed before FFmpeg:', error);
      reject(error);
    }
  });
});

ipcMain.handle('export-video', async (_event, options: {
  outputPath: string;
  clips: Array<{ filePath: string; startTime: number; duration: number; trimStart: number; trimEnd: number }>;
  resolution?: { width: number; height: number };
  format?: string;
  quality?: 'low' | 'medium' | 'high' | 'ultra';
}) => {
  return new Promise((resolve) => {
    const { outputPath, clips, resolution, quality = 'high' } = options;

    // Quality settings
    const qualitySettings = {
      low: { crf: 28, preset: 'fast' },
      medium: { crf: 23, preset: 'medium' },
      high: { crf: 18, preset: 'slow' },
      ultra: { crf: 15, preset: 'veryslow' },
    };

    const { crf, preset } = qualitySettings[quality];

    // For now, handle single clip export
    // TODO: Implement complex timeline with multiple clips and transitions
    if (clips.length === 1) {
      const clip = clips[0];
      const command = ffmpeg(clip.filePath)
        .setStartTime(clip.trimStart)
        .setDuration(clip.duration)
        .videoCodec('libx264')
        .outputOptions([
          `-crf ${crf}`,
          `-preset ${preset}`,
          '-movflags +faststart',
        ]);

      if (resolution) {
        command.size(`${resolution.width}x${resolution.height}`);
      }

      command
        .on('start', (commandLine) => {
          console.log('FFmpeg command:', commandLine);
        })
        .on('progress', (progress) => {
          if (editorWindow) {
            editorWindow.webContents.send('export-progress', progress.percent || 0);
          }
        })
        .on('end', () => {
          resolve({ success: true, outputPath });
        })
        .on('error', (error) => {
          console.error('Export error:', error);
          resolve({ success: false, error: String(error) });
        })
        .save(outputPath);
    } else {
      // TODO: Implement complex multi-clip timeline export
      resolve({ success: false, error: 'Multi-clip export not yet implemented' });
    }
  });
});

ipcMain.handle('show-save-dialog', async (_event, options: {
  title?: string;
  defaultPath?: string;
  filters?: Array<{ name: string; extensions: string[] }>;
}) => {
  const result = await dialog.showSaveDialog({
    title: options.title || 'Save File',
    defaultPath: options.defaultPath || `export-${Date.now()}.mp4`,
    filters: options.filters || [{ name: 'Video', extensions: ['mp4'] }],
  });

  return result;
});

// Helper function to get media metadata
function getMediaMetadata(filePath: string): Promise<{
  type: 'video' | 'audio' | 'image';
  duration: number;
  width?: number;
  height?: number;
}> {
  return new Promise((resolve, reject) => {
    const ext = path.extname(filePath).toLowerCase();

    // Determine type by extension
    const videoExts = ['.mp4', '.mov', '.avi', '.mkv', '.webm'];
    const audioExts = ['.mp3', '.wav', '.aac', '.ogg', '.m4a'];
    const imageExts = ['.jpg', '.jpeg', '.png', '.gif', '.webp'];

    let type: 'video' | 'audio' | 'image';
    if (videoExts.includes(ext)) type = 'video';
    else if (audioExts.includes(ext)) type = 'audio';
    else if (imageExts.includes(ext)) type = 'image';
    else type = 'video'; // default

    if (type === 'image') {
      // Images don't have duration, return static metadata
      resolve({ type, duration: 5, width: 0, height: 0 });
      return;
    }

    console.log('Running ffprobe on:', filePath);
    ffmpeg.ffprobe(filePath, (error, metadata) => {
      if (error) {
        console.error('FFprobe error for file:', filePath);
        console.error('FFprobe error details:', error);
        reject(error);
        return;
      }

      console.log('FFprobe successful for:', filePath);
      const videoStream = metadata.streams.find((s) => s.codec_type === 'video');
      const duration = metadata.format.duration || 0;

      resolve({
        type,
        duration,
        width: videoStream?.width,
        height: videoStream?.height,
      });
    });
  });
}

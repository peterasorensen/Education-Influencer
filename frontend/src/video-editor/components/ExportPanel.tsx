import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { FFmpeg } from '@ffmpeg/ffmpeg';
import { fetchFile, toBlobURL } from '@ffmpeg/util';
import { useEditorStore } from '../store';

interface ExportPanelProps {
  onClose: () => void;
}

const Overlay = styled.div`
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease-out;

  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }
`;

const Panel = styled.div`
  width: 600px;
  max-width: 90vw;
  max-height: 80vh;
  background: #151515;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: slideUp 0.3s ease-out;

  @keyframes slideUp {
    from {
      transform: translateY(20px);
      opacity: 0;
    }
    to {
      transform: translateY(0);
      opacity: 1;
    }
  }
`;

const Header = styled.div`
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Title = styled.h2`
  font-size: 18px;
  font-weight: 600;
  color: #ffffff;
  margin: 0;
`;

const CloseButton = styled.button`
  width: 32px;
  height: 32px;
  border-radius: 9999px;
  background: transparent;
  border: none;
  color: #a3a3a3;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 150ms cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    background: #1f1f1f;
    color: #ffffff;
  }
`;

const Content = styled.div`
  padding: 24px;
  overflow-y: auto;
  flex: 1;

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: #1f1f1f;
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;

    &:hover {
      background: rgba(124, 58, 237, 0.3);
    }
  }
`;

const Section = styled.div`
  margin-bottom: 24px;

  &:last-child {
    margin-bottom: 0;
  }
`;

const Label = styled.label`
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #ffffff;
  margin-bottom: 8px;
`;

const Select = styled.select`
  width: 100%;
  padding: 10px 12px;
  background: #1f1f1f;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: #ffffff;
  font-size: 14px;
  cursor: pointer;
  transition: all 150ms cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    border-color: rgba(124, 58, 237, 0.3);
  }

  &:focus {
    outline: none;
    border-color: #7c3aed;
    box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.5);
  }
`;

const Input = styled.input`
  width: 100%;
  padding: 10px 12px;
  background: #1f1f1f;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: #ffffff;
  font-size: 14px;
  transition: all 150ms cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    border-color: rgba(124, 58, 237, 0.3);
  }

  &:focus {
    outline: none;
    border-color: #7c3aed;
    box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.5);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const RadioGroup = styled.div`
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
`;

const RadioOption = styled.label<{ $selected: boolean }>`
  flex: 1;
  min-width: 120px;
  padding: 12px;
  background: ${({ $selected }) =>
    $selected ? '#7c3aed' : '#1f1f1f'};
  border: 2px solid
    ${({ $selected }) =>
      $selected ? '#8b5cf6' : 'rgba(255, 255, 255, 0.1)'};
  border-radius: 6px;
  cursor: pointer;
  transition: all 150ms cubic-bezier(0.4, 0, 0.2, 1);
  text-align: center;
  font-size: 13px;
  font-weight: 500;
  color: #ffffff;

  &:hover {
    border-color: #7c3aed;
    background: ${({ $selected }) =>
      $selected ? '#8b5cf6' : 'rgba(20, 20, 20, 0.85)'};
  }

  input {
    display: none;
  }
`;

const Footer = styled.div`
  padding: 20px 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  gap: 12px;
  justify-content: flex-end;
`;

const Button = styled.button<{ $variant?: 'primary' | 'secondary' }>`
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 150ms cubic-bezier(0.4, 0, 0.2, 1);
  border: none;

  ${({ $variant = 'secondary' }) =>
    $variant === 'primary'
      ? `
          background: #7c3aed;
          color: #ffffff;

          &:hover {
            background: #8b5cf6;
            box-shadow: 0 0 20px rgba(124, 58, 237, 0.4);
          }
        `
      : `
          background: #1f1f1f;
          color: #ffffff;
          border: 1px solid rgba(255, 255, 255, 0.1);

          &:hover {
            background: rgba(20, 20, 20, 0.85);
            border-color: rgba(124, 58, 237, 0.3);
          }
        `}

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const ProgressBar = styled.div<{ $progress: number }>`
  width: 100%;
  height: 8px;
  background: #1f1f1f;
  border-radius: 9999px;
  overflow: hidden;
  margin-top: 8px;

  &::after {
    content: '';
    display: block;
    width: ${({ $progress }) => $progress}%;
    height: 100%;
    background: #7c3aed;
    transition: width 0.3s ease-out;
    box-shadow: 0 0 10px rgba(124, 58, 237, 0.5);
  }
`;

const ProgressText = styled.div`
  font-size: 13px;
  color: #a3a3a3;
  margin-top: 8px;
  text-align: center;
`;

const StatusText = styled.div`
  font-size: 12px;
  color: #737373;
  margin-top: 4px;
  text-align: center;
  min-height: 18px;
`;

// Quality to CRF mapping
const QUALITY_CRF_MAP = {
  low: 28,
  medium: 23,
  high: 18,
  ultra: 15,
};

const ExportPanel: React.FC<ExportPanelProps> = ({ onClose }) => {
  const { mediaItems, tracks, exportProgress, isExporting, setExportProgress, setIsExporting } =
    useEditorStore();

  const [format, setFormat] = useState<string>('mp4');
  const [quality, setQuality] = useState<'low' | 'medium' | 'high' | 'ultra'>('high');
  const [resolution, setResolution] = useState<string>('original');
  const [customWidth, setCustomWidth] = useState<string>('1920');
  const [customHeight, setCustomHeight] = useState<string>('1080');
  const [ffmpegLoaded, setFfmpegLoaded] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');

  const ffmpegRef = useRef<FFmpeg | null>(null);

  useEffect(() => {
    loadFFmpeg();
  }, []);

  const loadFFmpeg = async () => {
    try {
      setStatusMessage('Loading FFmpeg...');
      const ffmpeg = new FFmpeg();
      
      ffmpeg.on('log', ({ message }) => {
        console.log('[FFmpeg]', message);
      });

      ffmpeg.on('progress', ({ progress, time }) => {
        const percentage = Math.min(progress * 100, 100);
        setExportProgress(percentage);
        setStatusMessage(`Processing: ${time / 1000000}s`);
      });

      const baseURL = 'https://unpkg.com/@ffmpeg/core@0.12.6/dist/umd';
      await ffmpeg.load({
        coreURL: await toBlobURL(`${baseURL}/ffmpeg-core.js`, 'text/javascript'),
        wasmURL: await toBlobURL(`${baseURL}/ffmpeg-core.wasm`, 'application/wasm'),
      });

      ffmpegRef.current = ffmpeg;
      setFfmpegLoaded(true);
      setStatusMessage('FFmpeg ready');
    } catch (error) {
      console.error('Failed to load FFmpeg:', error);
      setStatusMessage('Failed to load FFmpeg');
      alert('Failed to load FFmpeg. Please refresh the page and try again.');
    }
  };

  const handleExport = async () => {
    if (isExporting || !ffmpegLoaded || !ffmpegRef.current) {
      if (!ffmpegLoaded) {
        alert('FFmpeg is still loading. Please wait...');
      }
      return;
    }

    try {
      setIsExporting(true);
      setExportProgress(0);
      setStatusMessage('Preparing export...');

      // Collect all clips from all video tracks
      const clips = [];
      for (const track of tracks) {
        if (track.type === 'video' && track.visible) {
          for (const clip of track.clips) {
            const mediaItem = mediaItems.find((m) => m.id === clip.mediaItemId);
            if (mediaItem) {
              clips.push({
                mediaItem,
                clip,
              });
            }
          }
        }
      }

      if (clips.length === 0) {
        alert('No video clips to export');
        setIsExporting(false);
        setStatusMessage('');
        return;
      }

      const ffmpeg = ffmpegRef.current;

      // Sort clips by start time
      clips.sort((a, b) => a.clip.startTime - b.clip.startTime);

      setStatusMessage('Loading media files...');

      // Load all media files into FFmpeg's virtual file system
      for (let i = 0; i < clips.length; i++) {
        const { mediaItem } = clips[i];
        const fileData = await fetchFile(mediaItem.filePath);
        const ext = mediaItem.name.split('.').pop() || 'mp4';
        await ffmpeg.writeFile(`input${i}.${ext}`, fileData);
      }

      setStatusMessage('Building export command...');

      // Build FFmpeg command
      const ffmpegArgs: string[] = [];
      
      // For simplicity, if we have only one clip, just process it
      // For multiple clips, we'll concatenate them
      if (clips.length === 1) {
        const { clip } = clips[0];
        ffmpegArgs.push('-i', 'input0.mp4');
        
        // Apply trimming
        if (clip.trimStart > 0 || clip.trimEnd > 0) {
          ffmpegArgs.push('-ss', clip.trimStart.toString());
          const duration = clip.duration - clip.trimStart - clip.trimEnd;
          ffmpegArgs.push('-t', duration.toString());
        }
      } else {
        // Create concat file
        let concatContent = '';
        for (let i = 0; i < clips.length; i++) {
          const ext = clips[i].mediaItem.name.split('.').pop() || 'mp4';
          concatContent += `file 'input${i}.${ext}'\n`;
        }
        await ffmpeg.writeFile('concat.txt', concatContent);
        
        ffmpegArgs.push('-f', 'concat', '-safe', '0', '-i', 'concat.txt');
      }

      // Calculate resolution
      if (resolution !== 'original') {
        let width: number, height: number;
        
        if (resolution === 'custom') {
          width = parseInt(customWidth);
          height = parseInt(customHeight);
        } else {
          [width, height] = resolution.split('x').map(Number);
        }
        
        ffmpegArgs.push('-vf', `scale=${width}:${height}`);
      }

      // Set codec and quality based on format
      if (format === 'mp4') {
        ffmpegArgs.push('-c:v', 'libx264');
        ffmpegArgs.push('-crf', QUALITY_CRF_MAP[quality].toString());
        ffmpegArgs.push('-preset', 'medium');
        ffmpegArgs.push('-c:a', 'aac');
      } else if (format === 'webm') {
        ffmpegArgs.push('-c:v', 'libvpx-vp9');
        ffmpegArgs.push('-crf', QUALITY_CRF_MAP[quality].toString());
        ffmpegArgs.push('-b:v', '0');
        ffmpegArgs.push('-c:a', 'libopus');
      }

      ffmpegArgs.push(`output.${format}`);

      setStatusMessage('Processing video...');

      // Execute FFmpeg
      await ffmpeg.exec(ffmpegArgs);

      setStatusMessage('Finalizing export...');

      // Read the output file
      const data = await ffmpeg.readFile(`output.${format}`);

      // Create download link
      const blob = new Blob([data as BlobPart], {
        type: format === 'mp4' ? 'video/mp4' : 'video/webm'
      });
      const url = URL.createObjectURL(blob);
      
      const a = document.createElement('a');
      a.href = url;
      a.download = `export-${Date.now()}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      // Clean up
      for (let i = 0; i < clips.length; i++) {
        const ext = clips[i].mediaItem.name.split('.').pop() || 'mp4';
        await ffmpeg.deleteFile(`input${i}.${ext}`);
      }
      if (clips.length > 1) {
        await ffmpeg.deleteFile('concat.txt');
      }
      await ffmpeg.deleteFile(`output.${format}`);

      setStatusMessage('Export complete!');
      setExportProgress(100);
      
      setTimeout(() => {
        onClose();
      }, 1000);

    } catch (error) {
      console.error('Export error:', error);
      setStatusMessage('Export failed');
      alert(`Export failed: ${error}`);
    } finally {
      setTimeout(() => {
        setIsExporting(false);
        setExportProgress(0);
        setStatusMessage('');
      }, 1000);
    }
  };

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget && !isExporting) {
      onClose();
    }
  };

  return (
    <Overlay onClick={handleOverlayClick}>
      <Panel>
        <Header>
          <Title>Export Video</Title>
          {!isExporting && (
            <CloseButton onClick={onClose}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </CloseButton>
          )}
        </Header>

        <Content>
          <Section>
            <Label>Format</Label>
            <Select value={format} onChange={(e) => setFormat(e.target.value)} disabled={isExporting}>
              <option value="mp4">MP4 (H.264)</option>
              <option value="webm">WebM (VP9)</option>
            </Select>
          </Section>

          <Section>
            <Label>Quality</Label>
            <RadioGroup>
              {(['low', 'medium', 'high', 'ultra'] as const).map((q) => (
                <RadioOption key={q} $selected={quality === q}>
                  <input
                    type="radio"
                    name="quality"
                    value={q}
                    checked={quality === q}
                    onChange={(e) => setQuality(e.target.value as typeof quality)}
                    disabled={isExporting}
                  />
                  {q.charAt(0).toUpperCase() + q.slice(1)}
                </RadioOption>
              ))}
            </RadioGroup>
          </Section>

          <Section>
            <Label>Resolution</Label>
            <Select
              value={resolution}
              onChange={(e) => setResolution(e.target.value)}
              disabled={isExporting}
            >
              <option value="original">Original</option>
              <option value="3840x2160">4K (3840x2160)</option>
              <option value="2560x1440">QHD (2560x1440)</option>
              <option value="1920x1080">Full HD (1920x1080)</option>
              <option value="1280x720">HD (1280x720)</option>
              <option value="custom">Custom</option>
            </Select>
          </Section>

          {resolution === 'custom' && (
            <Section>
              <Label>Custom Resolution</Label>
              <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                <Input
                  type="number"
                  placeholder="Width"
                  value={customWidth}
                  onChange={(e) => setCustomWidth(e.target.value)}
                  disabled={isExporting}
                />
                <span style={{ color: '#737373' }}>×</span>
                <Input
                  type="number"
                  placeholder="Height"
                  value={customHeight}
                  onChange={(e) => setCustomHeight(e.target.value)}
                  disabled={isExporting}
                />
              </div>
            </Section>
          )}

          {(isExporting || !ffmpegLoaded) && (
            <Section>
              <Label>{isExporting ? 'Exporting...' : 'Loading...'}</Label>
              <ProgressBar $progress={exportProgress} />
              <ProgressText>{Math.round(exportProgress)}% complete</ProgressText>
              <StatusText>{statusMessage}</StatusText>
            </Section>
          )}
        </Content>

        <Footer>
          <Button onClick={onClose} disabled={isExporting}>
            Cancel
          </Button>
          <Button 
            $variant="primary" 
            onClick={handleExport} 
            disabled={isExporting || !ffmpegLoaded}
          >
            {isExporting ? 'Exporting...' : !ffmpegLoaded ? 'Loading...' : 'Export'}
          </Button>
        </Footer>
      </Panel>
    </Overlay>
  );
};

export default ExportPanel;

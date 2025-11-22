import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
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
  background: ${({ theme }) => theme.colors.background.secondary};
  border: 1px solid ${({ theme }) => theme.colors.border.primary};
  border-radius: ${({ theme }) => theme.borderRadius.lg};
  box-shadow: ${({ theme }) => theme.shadows.lg};
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
  border-bottom: 1px solid ${({ theme }) => theme.colors.border.primary};
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Title = styled.h2`
  font-size: 18px;
  font-weight: 600;
  color: ${({ theme }) => theme.colors.text.primary};
  margin: 0;
`;

const CloseButton = styled.button`
  width: 32px;
  height: 32px;
  border-radius: ${({ theme }) => theme.borderRadius.full};
  background: transparent;
  border: none;
  color: ${({ theme }) => theme.colors.text.secondary};
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all ${({ theme }) => theme.transitions.fast};

  &:hover {
    background: ${({ theme }) => theme.colors.background.tertiary};
    color: ${({ theme }) => theme.colors.text.primary};
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
    background: ${({ theme }) => theme.colors.background.tertiary};
  }

  &::-webkit-scrollbar-thumb {
    background: ${({ theme }) => theme.colors.border.primary};
    border-radius: 3px;

    &:hover {
      background: ${({ theme }) => theme.colors.border.accent};
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
  color: ${({ theme }) => theme.colors.text.primary};
  margin-bottom: 8px;
`;

const Select = styled.select`
  width: 100%;
  padding: 10px 12px;
  background: ${({ theme }) => theme.colors.background.tertiary};
  border: 1px solid ${({ theme }) => theme.colors.border.primary};
  border-radius: ${({ theme }) => theme.borderRadius.sm};
  color: ${({ theme }) => theme.colors.text.primary};
  font-size: 14px;
  cursor: pointer;
  transition: all ${({ theme }) => theme.transitions.fast};

  &:hover {
    border-color: ${({ theme }) => theme.colors.border.accent};
  }

  &:focus {
    outline: none;
    border-color: ${({ theme }) => theme.colors.accent.primary};
    box-shadow: 0 0 0 3px ${({ theme }) => theme.colors.accent.glow};
  }
`;

const Input = styled.input`
  width: 100%;
  padding: 10px 12px;
  background: ${({ theme }) => theme.colors.background.tertiary};
  border: 1px solid ${({ theme }) => theme.colors.border.primary};
  border-radius: ${({ theme }) => theme.borderRadius.sm};
  color: ${({ theme }) => theme.colors.text.primary};
  font-size: 14px;
  transition: all ${({ theme }) => theme.transitions.fast};

  &:hover {
    border-color: ${({ theme }) => theme.colors.border.accent};
  }

  &:focus {
    outline: none;
    border-color: ${({ theme }) => theme.colors.accent.primary};
    box-shadow: 0 0 0 3px ${({ theme }) => theme.colors.accent.glow};
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
  background: ${({ $selected, theme }) =>
    $selected ? theme.colors.accent.primary : theme.colors.background.tertiary};
  border: 2px solid
    ${({ $selected, theme }) =>
      $selected ? theme.colors.accent.hover : theme.colors.border.primary};
  border-radius: ${({ theme }) => theme.borderRadius.sm};
  cursor: pointer;
  transition: all ${({ theme }) => theme.transitions.fast};
  text-align: center;
  font-size: 13px;
  font-weight: 500;
  color: ${({ theme }) => theme.colors.text.primary};

  &:hover {
    border-color: ${({ theme }) => theme.colors.accent.primary};
    background: ${({ $selected, theme }) =>
      $selected ? theme.colors.accent.hover : theme.colors.background.glass};
  }

  input {
    display: none;
  }
`;

const Footer = styled.div`
  padding: 20px 24px;
  border-top: 1px solid ${({ theme }) => theme.colors.border.primary};
  display: flex;
  gap: 12px;
  justify-content: flex-end;
`;

const Button = styled.button<{ $variant?: 'primary' | 'secondary' }>`
  padding: 10px 20px;
  border-radius: ${({ theme }) => theme.borderRadius.sm};
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all ${({ theme }) => theme.transitions.fast};
  border: none;

  ${({ $variant = 'secondary', theme }) =>
    $variant === 'primary'
      ? `
          background: ${theme.colors.accent.primary};
          color: ${theme.colors.text.primary};

          &:hover {
            background: ${theme.colors.accent.hover};
            box-shadow: ${theme.shadows.glow};
          }
        `
      : `
          background: ${theme.colors.background.tertiary};
          color: ${theme.colors.text.primary};
          border: 1px solid ${theme.colors.border.primary};

          &:hover {
            background: ${theme.colors.background.glass};
            border-color: ${theme.colors.border.accent};
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
  background: ${({ theme }) => theme.colors.background.tertiary};
  border-radius: ${({ theme }) => theme.borderRadius.full};
  overflow: hidden;
  margin-top: 8px;

  &::after {
    content: '';
    display: block;
    width: ${({ $progress }) => $progress}%;
    height: 100%;
    background: ${({ theme }) => theme.colors.accent.primary};
    transition: width 0.3s ease-out;
    box-shadow: 0 0 10px ${({ theme }) => theme.colors.accent.glow};
  }
`;

const ProgressText = styled.div`
  font-size: 13px;
  color: ${({ theme }) => theme.colors.text.secondary};
  margin-top: 8px;
  text-align: center;
`;

const ExportPanel: React.FC<ExportPanelProps> = ({ onClose }) => {
  const { mediaItems, tracks, exportProgress, isExporting, setExportProgress, setIsExporting } =
    useEditorStore();

  const [format, setFormat] = useState<string>('mp4');
  const [quality, setQuality] = useState<'low' | 'medium' | 'high' | 'ultra'>('high');
  const [resolution, setResolution] = useState<string>('original');
  const [customWidth, setCustomWidth] = useState<string>('1920');
  const [customHeight, setCustomHeight] = useState<string>('1080');

  useEffect(() => {
    // Listen for export progress
    window.electronAPI.onExportProgress((progress) => {
      setExportProgress(progress);
    });
  }, [setExportProgress]);

  const handleExport = async () => {
    if (isExporting) return;

    // Show save dialog
    const result = await window.electronAPI.showSaveDialog({
      title: 'Export Video',
      defaultPath: `clip-forge-export-${Date.now()}.${format}`,
      filters: [
        { name: 'Video', extensions: [format] },
      ],
    });

    if (result.canceled || !result.filePath) {
      return;
    }

    setIsExporting(true);
    setExportProgress(0);

    try {
      // Collect all clips from all video tracks
      const clips = [];
      for (const track of tracks) {
        if (track.type === 'video' && track.visible) {
          for (const clip of track.clips) {
            const mediaItem = mediaItems.find((m) => m.id === clip.mediaItemId);
            if (mediaItem) {
              clips.push({
                filePath: mediaItem.filePath,
                startTime: clip.startTime,
                duration: clip.duration,
                trimStart: clip.trimStart,
                trimEnd: clip.trimEnd,
              });
            }
          }
        }
      }

      if (clips.length === 0) {
        alert('No video clips to export');
        setIsExporting(false);
        return;
      }

      // Calculate resolution
      let resolutionOption: { width: number; height: number } | undefined;
      if (resolution === 'custom') {
        resolutionOption = {
          width: parseInt(customWidth),
          height: parseInt(customHeight),
        };
      } else if (resolution !== 'original') {
        const [width, height] = resolution.split('x').map(Number);
        resolutionOption = { width, height };
      }

      // Export
      const exportResult = await window.electronAPI.exportVideo({
        outputPath: result.filePath,
        clips,
        resolution: resolutionOption,
        format,
        quality,
      });

      if (exportResult.success) {
        alert(`Video exported successfully to:\n${exportResult.outputPath}`);
        onClose();
      } else {
        alert(`Export failed: ${exportResult.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Export error:', error);
      alert(`Export failed: ${error}`);
    } finally {
      setIsExporting(false);
      setExportProgress(0);
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
              <option value="mov">MOV (QuickTime)</option>
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

          {isExporting && (
            <Section>
              <Label>Exporting...</Label>
              <ProgressBar $progress={exportProgress} />
              <ProgressText>{Math.round(exportProgress)}% complete</ProgressText>
            </Section>
          )}
        </Content>

        <Footer>
          <Button onClick={onClose} disabled={isExporting}>
            Cancel
          </Button>
          <Button $variant="primary" onClick={handleExport} disabled={isExporting}>
            {isExporting ? 'Exporting...' : 'Export'}
          </Button>
        </Footer>
      </Panel>
    </Overlay>
  );
};

export default ExportPanel;

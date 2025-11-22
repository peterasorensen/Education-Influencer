import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { useEditorStore } from '../store';
import VideoPlayer from './VideoPlayer';
import Timeline from './Timeline';
import MediaLibrary from './MediaLibrary';
import ExportPanel from './ExportPanel';
import ZoomEditor from './ZoomEditor';
import { PlayIcon, PauseIcon } from './Icons';

const EditorContainer = styled.div`
  width: 100vw;
  height: 100vh;
  background: ${({ theme }) => theme.colors.background.primary};
  display: flex;
  flex-direction: column;
  overflow: hidden;
`;

const Header = styled.header`
  height: 60px;
  background: ${({ theme }) => theme.colors.background.secondary};
  border-bottom: 1px solid ${({ theme }) => theme.colors.border.primary};
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  z-index: 10;
`;

const Title = styled.h1`
  font-size: 18px;
  font-weight: 600;
  color: ${({ theme }) => theme.colors.text.primary};
  margin: 0;
`;

const HeaderActions = styled.div`
  display: flex;
  gap: 12px;
  align-items: center;
`;

const Button = styled.button<{ $variant?: 'primary' | 'secondary' | 'danger' }>`
  padding: 8px 16px;
  border-radius: ${({ theme }) => theme.borderRadius.sm};
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all ${({ theme }) => theme.transitions.fast};
  border: none;
  outline: none;

  ${({ $variant = 'secondary', theme }) => {
    switch ($variant) {
      case 'primary':
        return `
          background: ${theme.colors.accent.primary};
          color: ${theme.colors.text.primary};

          &:hover {
            background: ${theme.colors.accent.hover};
            box-shadow: ${theme.shadows.glow};
          }
        `;
      case 'danger':
        return `
          background: ${theme.colors.status.recording};
          color: ${theme.colors.text.primary};

          &:hover {
            opacity: 0.9;
          }
        `;
      default:
        return `
          background: ${theme.colors.background.tertiary};
          color: ${theme.colors.text.primary};
          border: 1px solid ${theme.colors.border.primary};

          &:hover {
            background: ${theme.colors.background.glass};
            border-color: ${theme.colors.border.accent};
          }
        `;
    }
  }}

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const MainContent = styled.main`
  flex: 1;
  display: flex;
  overflow: hidden;
`;

const LeftPanelWrapper = styled.div<{ $collapsed: boolean }>`
  position: relative;
  display: flex;
  width: ${({ $collapsed }) => ($collapsed ? '0' : '280px')};
  transition: width ${({ theme }) => theme.transitions.normal};
`;

const LeftPanel = styled.aside`
  width: 280px;
  background: ${({ theme }) => theme.colors.background.secondary};
  border-right: 1px solid ${({ theme }) => theme.colors.border.primary};
  overflow-y: auto;

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

const CollapseButton = styled.button`
  position: absolute;
  top: 16px;
  right: -23px;
  width: 24px;
  height: 48px;
  background: ${({ theme }) => theme.colors.background.secondary};
  border: 1px solid ${({ theme }) => theme.colors.border.primary};
  border-radius: 0 ${({ theme }) => theme.borderRadius.sm} ${({ theme }) => theme.borderRadius.sm} 0;
  color: ${({ theme }) => theme.colors.text.secondary};
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 30;
  transition: all ${({ theme }) => theme.transitions.fast};
  box-shadow: 2px 0 4px rgba(0, 0, 0, 0.1);

  &:hover {
    background: ${({ theme }) => theme.colors.background.tertiary};
    border-color: ${({ theme }) => theme.colors.accent.primary};
    color: ${({ theme }) => theme.colors.text.primary};
    right: -24px;
  }

  svg {
    width: 14px;
    height: 14px;
  }
`;

const ExpandButton = styled.button`
  position: fixed;
  top: 80px;
  left: 12px;
  padding: 8px 12px;
  background: ${({ theme }) => theme.colors.background.secondary};
  border: 1px solid ${({ theme }) => theme.colors.border.primary};
  border-radius: ${({ theme }) => theme.borderRadius.sm};
  color: ${({ theme }) => theme.colors.text.secondary};
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  z-index: 30;
  transition: all ${({ theme }) => theme.transitions.fast};
  box-shadow: ${({ theme }) => theme.shadows.md};
  font-size: 13px;
  font-weight: 500;

  &:hover {
    background: ${({ theme }) => theme.colors.background.tertiary};
    border-color: ${({ theme }) => theme.colors.accent.primary};
    color: ${({ theme }) => theme.colors.text.primary};
    transform: translateX(2px);
    box-shadow: ${({ theme }) => theme.shadows.lg};
  }

  svg {
    width: 16px;
    height: 16px;
  }
`;

const CenterContent = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
`;

const PreviewArea = styled.div`
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: ${({ theme }) => theme.colors.background.primary};
  padding: 24px;
  overflow: auto;
`;

const TimelineArea = styled.div`
  height: 280px;
  background: ${({ theme }) => theme.colors.background.secondary};
  border-top: 1px solid ${({ theme }) => theme.colors.border.primary};
  display: flex;
  flex-direction: column;
`;

const PlaybackControls = styled.div`
  height: 60px;
  background: ${({ theme }) => theme.colors.background.tertiary};
  border-top: 1px solid ${({ theme }) => theme.colors.border.primary};
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 0 24px;
`;

const TimeDisplay = styled.div`
  font-family: 'Courier New', monospace;
  font-size: 14px;
  color: ${({ theme }) => theme.colors.text.secondary};
  min-width: 140px;
  text-align: center;
`;

const IconButton = styled.button<{ $active?: boolean }>`
  width: 40px;
  height: 40px;
  border-radius: ${({ theme }) => theme.borderRadius.full};
  background: ${({ $active, theme }) =>
    $active ? theme.colors.accent.primary : theme.colors.background.secondary};
  border: 1px solid ${({ theme }) => theme.colors.border.primary};
  color: ${({ theme }) => theme.colors.text.primary};
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all ${({ theme }) => theme.transitions.fast};

  &:hover {
    background: ${({ $active, theme }) =>
      $active ? theme.colors.accent.hover : theme.colors.background.tertiary};
    border-color: ${({ theme }) => theme.colors.border.accent};
    box-shadow: ${({ $active, theme }) => ($active ? theme.shadows.glow : 'none')};
  }
`;

const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: ${({ theme }) => theme.colors.text.secondary};
  gap: 16px;
  padding: 48px;
  text-align: center;

  h2 {
    font-size: 24px;
    font-weight: 600;
    color: ${({ theme }) => theme.colors.text.primary};
    margin: 0;
  }

  p {
    font-size: 14px;
    margin: 0;
    max-width: 400px;
  }
`;

const RightToolbar = styled.div`
  position: fixed;
  top: 60px;
  right: 0;
  bottom: 280px;
  width: 48px;
  background: ${({ theme }) => theme.colors.background.secondary};
  border-left: 1px solid ${({ theme }) => theme.colors.border.primary};
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px 0;
  gap: 8px;
  z-index: 20;
`;

const ToolbarButton = styled.button`
  width: 36px;
  height: 36px;
  border-radius: ${({ theme }) => theme.borderRadius.sm};
  background: ${({ theme }) => theme.colors.background.tertiary};
  border: 1px solid ${({ theme }) => theme.colors.border.primary};
  color: ${({ theme }) => theme.colors.text.secondary};
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all ${({ theme }) => theme.transitions.fast};

  &:hover {
    background: ${({ theme }) => theme.colors.background.glass};
    border-color: ${({ theme }) => theme.colors.accent.primary};
    color: ${({ theme }) => theme.colors.text.primary};
  }

  svg {
    width: 18px;
    height: 18px;
  }
`;

const RightPanelWrapper = styled.div`
  position: relative;
  display: flex;
`;

const ZoomEditorCollapseButton = styled.button`
  position: absolute;
  top: 16px;
  left: -23px;
  width: 24px;
  height: 48px;
  background: ${({ theme }) => theme.colors.background.secondary};
  border: 1px solid ${({ theme }) => theme.colors.border.primary};
  border-radius: ${({ theme }) => theme.borderRadius.sm} 0 0 ${({ theme }) => theme.borderRadius.sm};
  color: ${({ theme }) => theme.colors.text.secondary};
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 30;
  transition: all ${({ theme }) => theme.transitions.fast};
  box-shadow: -2px 0 4px rgba(0, 0, 0, 0.1);

  &:hover {
    background: ${({ theme }) => theme.colors.background.tertiary};
    border-color: ${({ theme }) => theme.colors.accent.primary};
    color: ${({ theme }) => theme.colors.text.primary};
    left: -24px;
  }

  svg {
    width: 14px;
    height: 14px;
  }
`;

export const VideoEditor: React.FC = () => {
  const {
    currentTime,
    isPlaying,
    duration,
    mediaItems,
    tracks,
    selectedClipIds,
    selectedZoomSegmentId,
    setIsPlaying,
    removeClip,
    removeZoomSegment,
    undo,
    redo,
    setSelectedZoomSegment,
  } = useEditorStore();

  const [showExportPanel, setShowExportPanel] = useState(false);
  const [isLibraryCollapsed, setIsLibraryCollapsed] = useState(false);
  const [isZoomEditorCollapsed, setIsZoomEditorCollapsed] = useState(false);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore if user is typing in an input
      const target = e.target as HTMLElement;
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
        return;
      }

      // Space for play/pause
      if (e.code === 'Space') {
        e.preventDefault();
        setIsPlaying(!isPlaying);
        return;
      }

      // Undo with CMD+Z (Mac) or Ctrl+Z (Windows/Linux)
      if ((e.metaKey || e.ctrlKey) && e.key === 'z' && !e.shiftKey) {
        e.preventDefault();
        undo();
        return;
      }

      // Redo with CMD+Shift+Z (Mac) or Ctrl+Shift+Z (Windows/Linux)
      if ((e.metaKey || e.ctrlKey) && e.key === 'z' && e.shiftKey) {
        e.preventDefault();
        redo();
        return;
      }

      // Delete selected clips or zoom segments with Backspace or Delete key
      if (e.key === 'Backspace' || e.key === 'Delete') {
        // Prevent default browser back navigation on Backspace
        e.preventDefault();

        // Delete selected zoom segment (takes priority)
        if (selectedZoomSegmentId) {
          removeZoomSegment(selectedZoomSegmentId);
          setSelectedZoomSegment(null);
          return;
        }

        // Delete all selected clips
        if (selectedClipIds.length > 0) {
          selectedClipIds.forEach((clipId) => {
            removeClip(clipId);
          });
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [
    isPlaying,
    selectedClipIds,
    selectedZoomSegmentId,
    setIsPlaying,
    removeClip,
    removeZoomSegment,
    setSelectedZoomSegment,
    undo,
    redo,
  ]);

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const formatTime = (seconds: number): string => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const hasContent = mediaItems.length > 0 || tracks.length > 0;

  return (
    <EditorContainer>
      <Header>
        <Title>Clip Forge Editor</Title>
        <HeaderActions>
          <Button
            $variant="primary"
            onClick={() => setShowExportPanel(true)}
            disabled={!hasContent}
          >
            Export
          </Button>
        </HeaderActions>
      </Header>

      <MainContent>
        {isLibraryCollapsed && (
          <ExpandButton
            onClick={() => setIsLibraryCollapsed(false)}
            title="Show Media Library"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="9 18 15 12 9 6" />
            </svg>
            <span>Media</span>
          </ExpandButton>
        )}
        <LeftPanelWrapper $collapsed={isLibraryCollapsed}>
          <LeftPanel>
            <MediaLibrary />
          </LeftPanel>
          {!isLibraryCollapsed && (
            <CollapseButton
              onClick={() => setIsLibraryCollapsed(true)}
              title="Hide Media Library"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="15 18 9 12 15 6" />
              </svg>
            </CollapseButton>
          )}
        </LeftPanelWrapper>

        <CenterContent>
          <PreviewArea>
            {hasContent ? (
              <VideoPlayer />
            ) : (
              <EmptyState>
                <h2>No Media Yet</h2>
                <p>
                  Import video clips, audio, or images to start editing your project
                </p>
                <Button $variant="primary">
                  Import Media
                </Button>
              </EmptyState>
            )}
          </PreviewArea>

          <TimelineArea>
            <PlaybackControls>
              <TimeDisplay>
                {formatTime(currentTime)} / {formatTime(duration)}
              </TimeDisplay>
              <IconButton $active={isPlaying} onClick={handlePlayPause}>
                {isPlaying ? <PauseIcon size={20} /> : <PlayIcon size={20} />}
              </IconButton>
            </PlaybackControls>
            <Timeline />
          </TimelineArea>
        </CenterContent>
      </MainContent>

      {showExportPanel && <ExportPanel onClose={() => setShowExportPanel(false)} />}
      {selectedZoomSegmentId && (
        <>
          {isZoomEditorCollapsed ? (
            <RightToolbar>
              <ToolbarButton
                onClick={() => setIsZoomEditorCollapsed(false)}
                title="Zoom Editor"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="11" cy="11" r="8" />
                  <path d="m21 21-4.35-4.35" />
                  <line x1="11" y1="8" x2="11" y2="14" />
                  <line x1="8" y1="11" x2="14" y2="11" />
                </svg>
              </ToolbarButton>
            </RightToolbar>
          ) : (
            <div style={{ position: 'fixed', top: 60, right: 0, bottom: 0, zIndex: 20 }}>
              <RightPanelWrapper>
                <ZoomEditorCollapseButton
                  onClick={() => setIsZoomEditorCollapsed(true)}
                  title="Hide Zoom Editor"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="9 18 15 12 9 6" />
                  </svg>
                </ZoomEditorCollapseButton>
                <ZoomEditor
                  segmentId={selectedZoomSegmentId}
                  onClose={() => setSelectedZoomSegment(null)}
                  isCollapsed={isZoomEditorCollapsed}
                  onToggleCollapse={() => setIsZoomEditorCollapsed(!isZoomEditorCollapsed)}
                />
              </RightPanelWrapper>
            </div>
          )}
        </>
      )}
    </EditorContainer>
  );
};

export default VideoEditor;

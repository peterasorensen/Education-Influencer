import React, { useState, useRef } from 'react';
import styled from 'styled-components';
import { useEditorStore, MediaItem, TimelineClip, TimelineTrack } from '../store';

const LibraryContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
`;

const LibraryHeader = styled.div`
  padding: 16px;
  border-bottom: 1px solid ${({ theme }) => theme.colors.border.primary};
`;

const Title = styled.h2`
  font-size: 14px;
  font-weight: 600;
  color: ${({ theme }) => theme.colors.text.primary};
  margin: 0 0 12px 0;
`;

const ImportButton = styled.button`
  width: 100%;
  padding: 10px;
  border-radius: ${({ theme }) => theme.borderRadius.sm};
  background: ${({ theme }) => theme.colors.accent.primary};
  color: ${({ theme }) => theme.colors.text.primary};
  border: none;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all ${({ theme }) => theme.transitions.fast};

  &:hover {
    background: ${({ theme }) => theme.colors.accent.hover};
    box-shadow: ${({ theme }) => theme.shadows.glow};
  }
`;

const MediaList = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 8px;
  align-content: start;

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

const MediaItemElement = styled.div<{ $selected: boolean; $isDragging: boolean }>`
  position: relative;
  background: ${({ theme }) => theme.colors.background.tertiary};
  border: 2px solid
    ${({ $selected, theme }) =>
      $selected ? theme.colors.accent.primary : theme.colors.border.primary};
  border-radius: ${({ theme }) => theme.borderRadius.sm};
  padding: 6px;
  cursor: ${({ $isDragging }) => ($isDragging ? 'grabbing' : 'grab')};
  transition: all ${({ theme }) => theme.transitions.fast};
  opacity: ${({ $isDragging }) => ($isDragging ? 0.5 : 1)};
  display: flex;
  flex-direction: column;

  &:hover {
    border-color: ${({ theme }) => theme.colors.accent.primary};
    background: ${({ theme }) => theme.colors.background.glass};
  }
`;

const DeleteButton = styled.button`
  position: absolute;
  top: 4px;
  right: 4px;
  width: 20px;
  height: 20px;
  border-radius: ${({ theme }) => theme.borderRadius.full};
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(4px);
  border: 1px solid ${({ theme }) => theme.colors.border.primary};
  color: ${({ theme }) => theme.colors.text.primary};
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  opacity: 0;
  transition: all ${({ theme }) => theme.transitions.fast};
  z-index: 10;

  ${MediaItemElement}:hover & {
    opacity: 1;
  }

  &:hover {
    background: ${({ theme }) => theme.colors.status.recording};
    border-color: ${({ theme }) => theme.colors.status.recording};
    transform: scale(1.15);
  }

  svg {
    width: 11px;
    height: 11px;
  }
`;

const MediaThumbnail = styled.div<{ $thumbnail?: string }>`
  width: 100%;
  aspect-ratio: 16 / 9;
  background: ${({ $thumbnail, theme }) =>
    $thumbnail
      ? `url(${$thumbnail}) center/cover no-repeat`
      : theme.colors.background.primary};
  border-radius: ${({ theme }) => theme.borderRadius.sm};
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${({ theme }) => theme.colors.text.muted};
  font-size: 9px;
`;

const MediaInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2px;
`;

const MediaName = styled.div`
  font-size: 10px;
  font-weight: 500;
  color: ${({ theme }) => theme.colors.text.primary};
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.2;
`;

const MediaMeta = styled.div`
  display: flex;
  justify-content: space-between;
  font-size: 9px;
  color: ${({ theme }) => theme.colors.text.muted};
  line-height: 1.2;
`;

const TypeBadge = styled.span<{ type: string }>`
  padding: 2px 4px;
  border-radius: ${({ theme }) => theme.borderRadius.sm};
  font-size: 8px;
  font-weight: 600;
  text-transform: uppercase;
  background: ${({ type, theme }) => {
    switch (type) {
      case 'video':
        return theme.colors.accent.primary;
      case 'audio':
        return theme.colors.status.warning;
      case 'image':
        return theme.colors.status.success;
      default:
        return theme.colors.background.glass;
    }
  }};
  color: ${({ theme }) => theme.colors.text.primary};
  line-height: 1;
`;

const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 24px;
  text-align: center;
  color: ${({ theme }) => theme.colors.text.muted};
  gap: 12px;

  svg {
    width: 48px;
    height: 48px;
    opacity: 0.3;
  }

  p {
    font-size: 12px;
    margin: 0;
  }
`;

const DropZone = styled.div<{ $isDragOver: boolean }>`
  position: absolute;
  inset: 0;
  background: ${({ $isDragOver, theme }) =>
    $isDragOver
      ? `${theme.colors.accent.primary}20`
      : 'transparent'};
  border: 2px dashed
    ${({ $isDragOver, theme }) =>
      $isDragOver ? theme.colors.accent.primary : 'transparent'};
  border-radius: ${({ theme }) => theme.borderRadius.md};
  display: ${({ $isDragOver }) => ($isDragOver ? 'flex' : 'none')};
  align-items: center;
  justify-content: center;
  pointer-events: none;
  z-index: 100;
  transition: all ${({ theme }) => theme.transitions.fast};

  &::before {
    content: 'Drop files to import';
    font-size: 16px;
    font-weight: 600;
    color: ${({ theme }) => theme.colors.accent.primary};
  }
`;

const MediaLibrary: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [draggingItemId, setDraggingItemId] = useState<string | null>(null);

  const {
    mediaItems,
    selectedMediaItemId,
    tracks,
    addMediaItem,
    removeMediaItem,
    setSelectedMediaItem,
    addTrack,
    addClip,
  } = useEditorStore();

  const handleImport = async () => {
    const result = await window.electronAPI.importMediaFiles();

    if (result.success && result.files) {
      for (const file of result.files) {
        // Generate thumbnail
        let thumbnail: string | undefined;
        if (file.type === 'video') {
          try {
            thumbnail = await window.electronAPI.generateThumbnail(file.filePath);
          } catch (error) {
            console.error('Failed to generate thumbnail:', error);
          }
        }

        const mediaItem: MediaItem = {
          id: `media-${Date.now()}-${Math.random()}`,
          name: file.name,
          type: file.type as 'video' | 'audio' | 'image',
          filePath: file.filePath,
          duration: file.duration,
          width: file.width,
          height: file.height,
          fileSize: file.fileSize,
          thumbnail,
        };

        addMediaItem(mediaItem);
      }
    }
  };

  const handleDragStart = (e: React.DragEvent, item: MediaItem) => {
    e.dataTransfer.effectAllowed = 'copy';
    e.dataTransfer.setData('mediaItemId', item.id);
    setDraggingItemId(item.id);
  };

  const handleDragEnd = () => {
    setDraggingItemId(null);
  };

  const handleItemClick = (itemId: string) => {
    setSelectedMediaItem(itemId);
  };

  const handleItemDoubleClick = (item: MediaItem) => {
    // Add to timeline on double-click
    // Only add video and audio to timeline (images will be supported later)
    if (item.type === 'image') {
      // TODO: Support image tracks
      return;
    }

    // Find or create appropriate track
    let targetTrack = tracks.find(
      (t) => t.type === item.type && !t.locked
    );

    if (!targetTrack) {
      // Create new track
      const newTrack: TimelineTrack = {
        id: `track-${Date.now()}`,
        type: item.type as 'video' | 'audio',
        name: `${item.type.charAt(0).toUpperCase() + item.type.slice(1)} ${
          tracks.filter((t) => t.type === item.type).length + 1
        }`,
        clips: [],
        locked: false,
        visible: true,
      };
      addTrack(newTrack);
      targetTrack = newTrack;
    }

    // TypeScript guard - should never happen at this point
    if (!targetTrack) return;

    // Calculate position (end of last clip or start)
    const lastClip = targetTrack.clips[targetTrack.clips.length - 1];
    const startTime = lastClip
      ? lastClip.startTime + lastClip.duration
      : 0;

    // Create clip
    const newClip: TimelineClip = {
      id: `clip-${Date.now()}`,
      mediaItemId: item.id,
      trackId: targetTrack.id,
      startTime,
      duration: item.duration,
      trimStart: 0,
      trimEnd: 0,
      volume: 1,
    };

    addClip(newClip);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);

    // Handle external file drops
    // Note: This would require additional implementation
    // for now, users can use the Import button
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const formatDuration = (seconds: number): string => {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const handleDelete = (e: React.MouseEvent, itemId: string) => {
    e.stopPropagation(); // Prevent item selection
    e.preventDefault(); // Prevent drag start

    if (confirm('Delete this media item? Any clips using it will also be removed.')) {
      removeMediaItem(itemId);
    }
  };

  return (
    <LibraryContainer
      ref={containerRef}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
    >
      <LibraryHeader>
        <Title>Media Library</Title>
        <ImportButton onClick={handleImport}>+ Import Media</ImportButton>
      </LibraryHeader>

      {mediaItems.length === 0 ? (
        <EmptyState>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="3" width="18" height="18" rx="2" />
            <circle cx="8.5" cy="8.5" r="1.5" fill="currentColor" />
            <path d="M21 15l-5-5L5 21" />
          </svg>
          <p>No media imported yet</p>
          <p>Click the button above to import files</p>
        </EmptyState>
      ) : (
        <MediaList>
          {mediaItems.map((item) => (
            <MediaItemElement
              key={item.id}
              $selected={selectedMediaItemId === item.id}
              $isDragging={draggingItemId === item.id}
              draggable
              onDragStart={(e) => handleDragStart(e, item)}
              onDragEnd={handleDragEnd}
              onClick={() => handleItemClick(item.id)}
              onDoubleClick={() => handleItemDoubleClick(item)}
            >
              <DeleteButton
                onClick={(e) => handleDelete(e, item.id)}
                onMouseDown={(e) => e.stopPropagation()} // Prevent drag start
                title="Delete media item"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </DeleteButton>
              <MediaThumbnail $thumbnail={item.thumbnail}>
                {!item.thumbnail && <TypeBadge type={item.type}>{item.type}</TypeBadge>}
              </MediaThumbnail>
              <MediaInfo>
                <MediaName title={item.name}>{item.name}</MediaName>
                <MediaMeta>
                  <span>{formatDuration(item.duration)}</span>
                  <span>{formatFileSize(item.fileSize)}</span>
                </MediaMeta>
              </MediaInfo>
            </MediaItemElement>
          ))}
        </MediaList>
      )}

      <DropZone $isDragOver={isDragOver} />
    </LibraryContainer>
  );
};

export default MediaLibrary;

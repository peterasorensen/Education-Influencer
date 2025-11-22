import React, { useRef, useEffect, useState } from 'react';
import styled from 'styled-components';
import { useEditorStore } from '../store';

const PlayerContainer = styled.div`
  width: 100%;
  max-width: 1200px;
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const PlayerControls = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 8px;
`;

const AspectRatioSelect = styled.select`
  padding: 6px 12px;
  border-radius: ${({ theme }) => theme.borderRadius.sm};
  background: ${({ theme }) => theme.colors.background.tertiary};
  color: ${({ theme }) => theme.colors.text.primary};
  border: 1px solid ${({ theme }) => theme.colors.border.primary};
  font-size: 13px;
  cursor: pointer;
  transition: all ${({ theme }) => theme.transitions.fast};

  &:hover {
    border-color: ${({ theme }) => theme.colors.border.accent};
    background: ${({ theme }) => theme.colors.background.glass};
  }

  &:focus {
    outline: none;
    border-color: ${({ theme }) => theme.colors.accent.primary};
  }
`;

const CropButton = styled.button<{ $active?: boolean }>`
  padding: 6px 12px;
  border-radius: ${({ theme }) => theme.borderRadius.sm};
  background: ${({ $active, theme }) =>
    $active ? theme.colors.accent.primary : theme.colors.background.tertiary};
  color: ${({ theme }) => theme.colors.text.primary};
  border: 1px solid ${({ $active, theme }) =>
    $active ? theme.colors.accent.primary : theme.colors.border.primary};
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all ${({ theme }) => theme.transitions.fast};

  &:hover {
    border-color: ${({ theme }) => theme.colors.accent.primary};
    background: ${({ $active, theme }) =>
      $active ? theme.colors.accent.hover : theme.colors.background.glass};
    box-shadow: ${({ $active, theme }) => ($active ? theme.shadows.glow : 'none')};
  }

  svg {
    width: 14px;
    height: 14px;
  }
`;

const VideoWrapper = styled.div<{ $aspectRatio?: string }>`
  position: relative;
  background: #000;
  border-radius: ${({ theme }) => theme.borderRadius.lg};
  overflow: hidden;
  box-shadow: ${({ theme }) => theme.shadows.lg};
  border: 1px solid ${({ theme }) => theme.colors.border.primary};
  width: 100%;
  ${({ $aspectRatio }) => $aspectRatio && `aspect-ratio: ${$aspectRatio};`}
  max-height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const VideoTransformContainer = styled.div<{
  $scale: number;
  $translateX: number;
  $translateY: number;
}>`
  width: 100%;
  height: 100%;
  transform: scale(${({ $scale }) => $scale})
             translate(${({ $translateX }) => $translateX}%, ${({ $translateY }) => $translateY}%);
  transform-origin: center center;
  transition: transform 0.25s cubic-bezier(0.4, 0.0, 0.2, 1);
`;

const Video = styled.video<{ $objectFit: 'contain' | 'cover' }>`
  width: 100%;
  height: 100%;
  display: block;
  object-fit: ${({ $objectFit }) => $objectFit};
`;

const VideoOverlay = styled.div<{ $show: boolean }>`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: ${({ $show }) => ($show ? 1 : 0)};
  pointer-events: ${({ $show }) => ($show ? 'auto' : 'none')};
  transition: opacity ${({ theme }) => theme.transitions.fast};
`;

const PlayButton = styled.button`
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: ${({ theme }) => theme.colors.accent.primary};
  border: none;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all ${({ theme }) => theme.transitions.fast};
  box-shadow: ${({ theme }) => theme.shadows.glow};

  &:hover {
    transform: scale(1.1);
    background: ${({ theme }) => theme.colors.accent.hover};
    box-shadow: ${({ theme }) => theme.shadows.glowLg};
  }

  svg {
    margin-left: 4px;
  }
`;

const PlayerInfo = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: ${({ theme }) => theme.colors.text.secondary};
  font-size: 13px;
  padding: 0 8px;
`;

const EmptyPlayer = styled.div`
  width: 100%;
  aspect-ratio: 16 / 9;
  background: ${({ theme }) => theme.colors.background.tertiary};
  border-radius: ${({ theme }) => theme.borderRadius.lg};
  border: 2px dashed ${({ theme }) => theme.colors.border.primary};
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: ${({ theme }) => theme.colors.text.muted};

  svg {
    width: 64px;
    height: 64px;
    opacity: 0.3;
  }

  p {
    font-size: 14px;
    margin: 0;
  }
`;

type AspectRatio = 'auto' | '16:9' | '9:16' | '4:3' | '1:1' | '21:9';

const VideoPlayer: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [showOverlay, setShowOverlay] = useState(false);
  const [videoSrc, setVideoSrc] = useState<string | null>(null);
  const [aspectRatio, setAspectRatio] = useState<AspectRatio>('auto');
  const [cropMode, setCropMode] = useState(false);
  const [videoDimensions, setVideoDimensions] = useState<{ width: number; height: number } | null>(null);

  const {
    currentTime,
    isPlaying,
    tracks,
    mediaItems,
    zoomSegments,
    setCurrentTime,
    setIsPlaying,
  } = useEditorStore();

  // Get the current clip being played
  useEffect(() => {
    if (tracks.length === 0 || mediaItems.length === 0) {
      setVideoSrc(null);
      return;
    }

    // Find the first video track
    const videoTrack = tracks.find((t) => t.type === 'video' && t.visible);
    if (!videoTrack) {
      setVideoSrc(null);
      return;
    }

    // Find clip at current time
    const currentClip = videoTrack.clips.find(
      (clip) =>
        currentTime >= clip.startTime &&
        currentTime < clip.startTime + clip.duration
    );

    if (!currentClip) {
      setVideoSrc(null);
      return;
    }

    // Find media item
    const mediaItem = mediaItems.find((item) => item.id === currentClip.mediaItemId);
    if (mediaItem && mediaItem.type === 'video') {
      // Use custom protocol to access local files
      setVideoSrc(`media-file://${mediaItem.filePath}`);
    }
  }, [currentTime, tracks, mediaItems]);

  // Handle play/pause
  useEffect(() => {
    if (!videoRef.current || !videoSrc) return;

    if (isPlaying) {
      videoRef.current.play().catch((err) => {
        console.error('Failed to play video:', err);
        setIsPlaying(false);
      });
    } else {
      videoRef.current.pause();
    }
  }, [isPlaying, videoSrc, setIsPlaying]);

  // Sync current time with video
  useEffect(() => {
    if (!videoRef.current || !videoSrc) return;

    const video = videoRef.current;
    const handleTimeUpdate = () => {
      // Sync with timeline
      if (Math.abs(video.currentTime - currentTime) > 0.1) {
        setCurrentTime(video.currentTime);
      }
    };

    const handleLoadedMetadata = () => {
      setVideoDimensions({ width: video.videoWidth, height: video.videoHeight });
    };

    const handleEnded = () => {
      setIsPlaying(false);
    };

    video.addEventListener('timeupdate', handleTimeUpdate);
    video.addEventListener('loadedmetadata', handleLoadedMetadata);
    video.addEventListener('ended', handleEnded);

    // Set initial time
    video.currentTime = currentTime;

    return () => {
      video.removeEventListener('timeupdate', handleTimeUpdate);
      video.removeEventListener('loadedmetadata', handleLoadedMetadata);
      video.removeEventListener('ended', handleEnded);
    };
  }, [videoSrc, currentTime, setCurrentTime, setIsPlaying]);

  const handleVideoClick = () => {
    setIsPlaying(!isPlaying);
  };

  const handleMouseEnter = () => {
    if (!isPlaying && videoSrc) {
      setShowOverlay(true);
    }
  };

  const handleMouseLeave = () => {
    setShowOverlay(false);
  };

  const getAspectRatioValue = (): string | undefined => {
    if (aspectRatio === 'auto') {
      if (videoDimensions) {
        return `${videoDimensions.width} / ${videoDimensions.height}`;
      }
      return undefined;
    }
    return aspectRatio.replace(':', ' / ');
  };

  // Helper function to interpolate cursor position
  const getCursorPositionAtTime = (
    cursorData: Array<{ x: number; y: number; timestamp: number }> | undefined,
    timeMs: number
  ): { x: number; y: number } | null => {
    if (!cursorData || cursorData.length === 0) {
      return null;
    }

    // Find the two closest positions
    let before = cursorData[0];
    let after = cursorData[cursorData.length - 1];

    for (let i = 0; i < cursorData.length - 1; i++) {
      if (cursorData[i].timestamp <= timeMs && cursorData[i + 1].timestamp >= timeMs) {
        before = cursorData[i];
        after = cursorData[i + 1];
        break;
      }
    }

    // If time is before first position, return first position
    if (timeMs <= cursorData[0].timestamp) {
      return { x: cursorData[0].x, y: cursorData[0].y };
    }

    // If time is after last position, return last position
    if (timeMs >= cursorData[cursorData.length - 1].timestamp) {
      return { x: after.x, y: after.y };
    }

    // Linear interpolation between before and after
    const t = (timeMs - before.timestamp) / (after.timestamp - before.timestamp);
    return {
      x: before.x + (after.x - before.x) * t,
      y: before.y + (after.y - before.y) * t,
    };
  };

  // Calculate current zoom transform
  const getZoomTransform = (): { scale: number; translateX: number; translateY: number } => {
    // Find active zoom segment at current time
    const activeZoom = zoomSegments.find(
      (segment) =>
        currentTime >= segment.startTime &&
        currentTime < segment.startTime + segment.duration
    );

    if (!activeZoom) {
      // No zoom active, return identity transform
      return { scale: 1.0, translateX: 0, translateY: 0 };
    }

    const scale = activeZoom.zoomLevel;

    // Calculate translation based on mode
    if (activeZoom.mode === 'manual') {
      // Manual mode: translate to targetX/Y position
      // Convert 0-1 coordinates to percentage translation
      // When zoomed in, we need to translate in the opposite direction
      // to make the target point appear centered
      const translateX = ((0.5 - (activeZoom.targetX || 0.5)) * 100) / scale;
      const translateY = ((0.5 - (activeZoom.targetY || 0.5)) * 100) / scale;
      return { scale, translateX, translateY };
    } else {
      // Auto mode: Use cursor tracking data
      // Find the current clip being played
      const videoTrack = tracks.find((t) => t.type === 'video' && t.visible);
      if (!videoTrack) {
        return { scale, translateX: 0, translateY: 0 };
      }

      const currentClip = videoTrack.clips.find(
        (clip) =>
          currentTime >= clip.startTime &&
          currentTime < clip.startTime + clip.duration
      );

      if (!currentClip) {
        return { scale, translateX: 0, translateY: 0 };
      }

      // Get media item with cursor data
      const mediaItem = mediaItems.find((item) => item.id === currentClip.mediaItemId);
      if (!mediaItem || !mediaItem.cursorData) {
        return { scale, translateX: 0, translateY: 0 };
      }

      // Calculate time within the clip (accounting for trim)
      const relativeTime = currentTime - currentClip.startTime;
      const timeInSource = (relativeTime + currentClip.trimStart) * 1000; // Convert to ms

      // Get interpolated cursor position
      const cursorPos = getCursorPositionAtTime(mediaItem.cursorData, timeInSource);
      if (!cursorPos || !videoDimensions) {
        return { scale, translateX: 0, translateY: 0 };
      }

      // Convert cursor position to normalized coordinates (0-1)
      const normalizedX = cursorPos.x / videoDimensions.width;
      const normalizedY = cursorPos.y / videoDimensions.height;

      // Translate to keep cursor centered
      const translateX = ((0.5 - normalizedX) * 100) / scale;
      const translateY = ((0.5 - normalizedY) * 100) / scale;

      return { scale, translateX, translateY };
    }
  };

  const zoomTransform = getZoomTransform();

  if (!videoSrc) {
    return (
      <PlayerContainer>
        <EmptyPlayer>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polygon points="5 3 19 12 5 21 5 3" />
          </svg>
          <p>No video to preview</p>
          <p>Add clips to the timeline to see preview</p>
        </EmptyPlayer>
      </PlayerContainer>
    );
  }

  return (
    <PlayerContainer>
      <PlayerControls>
        <AspectRatioSelect
          value={aspectRatio}
          onChange={(e) => setAspectRatio(e.target.value as AspectRatio)}
        >
          <option value="auto">Auto</option>
          <option value="16:9">16:9 (Landscape)</option>
          <option value="9:16">9:16 (Portrait)</option>
          <option value="4:3">4:3 (Classic)</option>
          <option value="1:1">1:1 (Square)</option>
          <option value="21:9">21:9 (Ultrawide)</option>
        </AspectRatioSelect>
        <CropButton
          $active={cropMode}
          onClick={() => setCropMode(!cropMode)}
          title={cropMode ? 'Crop to fill (active)' : 'Fit to contain'}
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M6.13 1L6 16a2 2 0 0 0 2 2h15" />
            <path d="M1 6.13L16 6a2 2 0 0 1 2 2v15" />
          </svg>
          {cropMode ? 'Fill' : 'Fit'}
        </CropButton>
      </PlayerControls>
      <VideoWrapper
        $aspectRatio={getAspectRatioValue()}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        onClick={handleVideoClick}
      >
        <VideoTransformContainer
          $scale={zoomTransform.scale}
          $translateX={zoomTransform.translateX}
          $translateY={zoomTransform.translateY}
        >
          <Video ref={videoRef} src={videoSrc} $objectFit={cropMode ? 'cover' : 'contain'} />
        </VideoTransformContainer>
        <VideoOverlay $show={showOverlay}>
          <PlayButton>
            <svg width="32" height="32" viewBox="0 0 24 24" fill="white">
              <polygon points="5 3 19 12 5 21 5 3" />
            </svg>
          </PlayButton>
        </VideoOverlay>
      </VideoWrapper>
      <PlayerInfo>
        <span>Preview</span>
        <span>
          {videoDimensions && `${videoDimensions.width}×${videoDimensions.height} • `}
          {tracks.length} track{tracks.length !== 1 ? 's' : ''} • {mediaItems.length} item
          {mediaItems.length !== 1 ? 's' : ''}
        </span>
      </PlayerInfo>
    </PlayerContainer>
  );
};

export default VideoPlayer;

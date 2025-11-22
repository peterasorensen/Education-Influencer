import React from 'react';
import styled from 'styled-components';
import { useEditorStore } from '../store';

const EditorPanel = styled.div`
  width: 320px;
  height: 100%;
  background: ${({ theme }) => theme.colors.background.secondary};
  border-left: 1px solid ${({ theme }) => theme.colors.border.primary};
  display: flex;
  flex-direction: column;
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

const EditorHeader = styled.div`
  padding: 20px;
  border-bottom: 1px solid ${({ theme }) => theme.colors.border.primary};
`;

const TitleText = styled.h2`
  font-size: 16px;
  font-weight: 600;
  color: ${({ theme }) => theme.colors.text.primary};
  margin: 0;
`;

const EditorContent = styled.div`
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

const Section = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const SectionLabel = styled.label`
  font-size: 13px;
  font-weight: 600;
  color: ${({ theme }) => theme.colors.text.primary};
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const SectionDescription = styled.p`
  font-size: 12px;
  color: ${({ theme }) => theme.colors.text.muted};
  margin: -8px 0 0 0;
  line-height: 1.5;
`;

const SliderContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const SliderTrack = styled.div`
  position: relative;
  width: 100%;
  height: 6px;
  background: ${({ theme }) => theme.colors.background.tertiary};
  border-radius: 3px;
  cursor: pointer;
`;

const SliderFill = styled.div<{ $percentage: number }>`
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  width: ${({ $percentage }) => $percentage}%;
  background: ${({ theme }) => theme.colors.accent.primary};
  border-radius: 3px;
  transition: width 0.05s ease;
`;

const SliderThumb = styled.div<{ $percentage: number }>`
  position: absolute;
  top: 50%;
  left: ${({ $percentage }) => $percentage}%;
  transform: translate(-50%, -50%);
  width: 20px;
  height: 20px;
  background: ${({ theme }) => theme.colors.accent.primary};
  border: 3px solid ${({ theme }) => theme.colors.background.secondary};
  border-radius: 50%;
  cursor: grab;
  box-shadow: ${({ theme }) => theme.shadows.md};
  transition: box-shadow ${({ theme }) => theme.transitions.fast};

  &:hover {
    box-shadow: ${({ theme }) => theme.shadows.glow};
  }

  &:active {
    cursor: grabbing;
  }
`;

const SliderLabel = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  color: ${({ theme }) => theme.colors.text.secondary};
`;

const SliderValue = styled.span`
  font-weight: 600;
  color: ${({ theme }) => theme.colors.text.primary};
  font-family: 'Courier New', monospace;
`;

const ResetButton = styled.button`
  padding: 0;
  background: none;
  border: none;
  color: ${({ theme }) => theme.colors.accent.primary};
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: color ${({ theme }) => theme.transitions.fast};

  &:hover {
    color: ${({ theme }) => theme.colors.accent.hover};
    text-decoration: underline;
  }
`;

const ModeToggle = styled.div`
  display: flex;
  gap: 8px;
  background: ${({ theme }) => theme.colors.background.tertiary};
  padding: 4px;
  border-radius: ${({ theme }) => theme.borderRadius.sm};
`;

const ModeButton = styled.button<{ $active: boolean }>`
  flex: 1;
  padding: 8px 16px;
  border-radius: ${({ theme }) => theme.borderRadius.sm};
  background: ${({ $active, theme }) =>
    $active ? theme.colors.accent.primary : 'transparent'};
  border: none;
  color: ${({ $active, theme }) =>
    $active ? theme.colors.text.primary : theme.colors.text.secondary};
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all ${({ theme }) => theme.transitions.fast};
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;

  &:hover {
    background: ${({ $active, theme }) =>
      $active ? theme.colors.accent.hover : theme.colors.background.glass};
    color: ${({ theme }) => theme.colors.text.primary};
  }

  svg {
    width: 14px;
    height: 14px;
  }
`;

const ModeDescription = styled.p`
  font-size: 12px;
  color: ${({ theme }) => theme.colors.text.muted};
  margin: 4px 0 0 0;
  line-height: 1.5;
`;

const ActionButton = styled.button`
  padding: 10px 16px;
  border-radius: ${({ theme }) => theme.borderRadius.sm};
  background: ${({ theme }) => theme.colors.background.tertiary};
  border: 1px solid ${({ theme }) => theme.colors.border.primary};
  color: ${({ theme }) => theme.colors.text.primary};
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all ${({ theme }) => theme.transitions.fast};
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;

  &:hover {
    background: ${({ theme }) => theme.colors.background.glass};
    border-color: ${({ theme }) => theme.colors.border.accent};
  }

  svg {
    width: 16px;
    height: 16px;
  }
`;

const PositionPicker = styled.div`
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  background: ${({ theme }) => theme.colors.background.tertiary};
  border-radius: ${({ theme }) => theme.borderRadius.sm};
  border: 2px solid ${({ theme }) => theme.colors.border.primary};
  cursor: crosshair;
  overflow: hidden;

  &:hover {
    border-color: ${({ theme }) => theme.colors.border.accent};
  }
`;

const PositionGrid = styled.div`
  position: absolute;
  inset: 0;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(3, 1fr);

  &::before,
  &::after {
    content: '';
    position: absolute;
    background: ${({ theme }) => theme.colors.border.primary};
    opacity: 0.3;
  }

  &::before {
    left: 33.333%;
    right: 33.333%;
    top: 0;
    bottom: 0;
    width: 1px;
  }

  &::after {
    left: 66.666%;
    top: 0;
    bottom: 0;
    width: 1px;
  }
`;

const PositionGridHorizontal = styled.div`
  position: absolute;
  left: 0;
  right: 0;
  height: 1px;
  background: ${({ theme }) => theme.colors.border.primary};
  opacity: 0.3;

  &:nth-child(1) {
    top: 33.333%;
  }

  &:nth-child(2) {
    top: 66.666%;
  }
`;

const PositionTarget = styled.div<{ $x: number; $y: number }>`
  position: absolute;
  left: ${({ $x }) => $x * 100}%;
  top: ${({ $y }) => $y * 100}%;
  transform: translate(-50%, -50%);
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: ${({ theme }) => theme.colors.accent.primary};
  border: 3px solid ${({ theme }) => theme.colors.background.secondary};
  box-shadow: ${({ theme }) => theme.shadows.md};
  pointer-events: none;

  &::before {
    content: '';
    position: absolute;
    inset: -8px;
    border-radius: 50%;
    border: 1px solid ${({ theme }) => theme.colors.accent.primary};
    opacity: 0.3;
  }
`;

const PositionLabel = styled.div`
  font-size: 11px;
  color: ${({ theme }) => theme.colors.text.muted};
  text-align: center;
  margin-top: 8px;
  font-family: 'Courier New', monospace;
`;

interface ZoomEditorProps {
  segmentId: string;
  onClose: () => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

const ZoomEditor: React.FC<ZoomEditorProps> = ({ segmentId, onClose: _onClose, isCollapsed: _isCollapsed, onToggleCollapse: _onToggleCollapse }) => {
  const { zoomSegments, updateZoomSegment } = useEditorStore();
  const segment = zoomSegments.find((s) => s.id === segmentId);

  if (!segment) {
    return null;
  }

  const zoomToPercentage = (zoomLevel: number) => {
    // Map 1.0-2.0 to 0-100%
    return ((zoomLevel - 1.0) / 1.0) * 100;
  };

  const percentageToZoom = (percentage: number) => {
    // Map 0-100% to 1.0-2.0
    return 1.0 + (percentage / 100) * 1.0;
  };

  const handleSliderMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();

    const sliderElement = e.currentTarget as HTMLElement;
    const rect = sliderElement.getBoundingClientRect();

    const updateZoom = (clientX: number) => {
      const x = Math.max(0, Math.min(clientX - rect.left, rect.width));
      const percentage = (x / rect.width) * 100;
      const newZoomLevel = percentageToZoom(percentage);
      updateZoomSegment(segmentId, { zoomLevel: Math.max(1.0, Math.min(newZoomLevel, 2.0)) });
    };

    updateZoom(e.clientX);

    const handleMouseMove = (e: MouseEvent) => {
      updateZoom(e.clientX);
    };

    const handleMouseUp = () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  const handleModeChange = (mode: 'auto' | 'manual') => {
    updateZoomSegment(segmentId, { mode });
  };

  const handleResetZoom = () => {
    updateZoomSegment(segmentId, { zoomLevel: 1.5 });
  };

  const handleApplyToAll = () => {
    // Apply current zoom level to all other zoom segments
    zoomSegments.forEach((seg) => {
      if (seg.id !== segmentId) {
        updateZoomSegment(seg.id, { zoomLevel: segment.zoomLevel });
      }
    });
  };

  const handlePositionClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width;
    const y = (e.clientY - rect.top) / rect.height;

    // Clamp values between 0 and 1
    const clampedX = Math.max(0, Math.min(1, x));
    const clampedY = Math.max(0, Math.min(1, y));

    updateZoomSegment(segmentId, {
      targetX: clampedX,
      targetY: clampedY,
    });
  };

  return (
    <EditorPanel>
      <EditorHeader>
        <TitleText>Zoom editor</TitleText>
      </EditorHeader>

      <EditorContent>
        <Section>
          <SectionLabel>Zoom level</SectionLabel>
          <SectionDescription>
            How close to zoom on the cursor during this zoom phase
          </SectionDescription>
          <SliderContainer>
            <SliderTrack onMouseDown={handleSliderMouseDown}>
              <SliderFill $percentage={zoomToPercentage(segment.zoomLevel)} />
              <SliderThumb $percentage={zoomToPercentage(segment.zoomLevel)} />
            </SliderTrack>
            <SliderLabel>
              <span>Zoom Level</span>
              <SliderValue>{segment.zoomLevel.toFixed(1)}x</SliderValue>
            </SliderLabel>
          </SliderContainer>
          <ResetButton onClick={handleResetZoom}>Reset</ResetButton>
        </Section>

        <Section>
          <ActionButton onClick={handleApplyToAll}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="3" width="7" height="7" rx="1" />
              <rect x="14" y="3" width="7" height="7" rx="1" />
              <rect x="14" y="14" width="7" height="7" rx="1" />
              <rect x="3" y="14" width="7" height="7" rx="1" />
            </svg>
            Apply zoom level to all other zooms
          </ActionButton>
        </Section>

        <Section>
          <SectionLabel>Zoom mode</SectionLabel>
          <ModeToggle>
            <ModeButton $active={segment.mode === 'auto'} onClick={() => handleModeChange('auto')}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 2L2 7l10 5 10-5-10-5z" />
                <path d="M2 17l10 5 10-5" />
                <path d="M2 12l10 5 10-5" />
              </svg>
              Auto
            </ModeButton>
            <ModeButton
              $active={segment.mode === 'manual'}
              onClick={() => handleModeChange('manual')}
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="3" />
                <path d="M12 1v6m0 6v6M5.64 5.64l4.24 4.24m4.24 4.24l4.24 4.24M1 12h6m6 0h6M5.64 18.36l4.24-4.24m4.24-4.24l4.24-4.24" />
              </svg>
              Manual
            </ModeButton>
          </ModeToggle>
          <ModeDescription>
            {segment.mode === 'auto'
              ? 'Zoomed camera will automatically try to keep the mouse cursor visible.'
              : 'Manually adjust where the camera zooms to with adjustable zoom controls.'}
          </ModeDescription>
        </Section>

        {segment.mode === 'manual' && (
          <Section>
            <SectionLabel>Zoom target position</SectionLabel>
            <SectionDescription>
              Click on the preview below to set where the camera should focus
            </SectionDescription>
            <PositionPicker onClick={handlePositionClick}>
              <PositionGrid>
                <PositionGridHorizontal />
                <PositionGridHorizontal />
              </PositionGrid>
              <PositionTarget
                $x={segment.targetX || 0.5}
                $y={segment.targetY || 0.5}
              />
            </PositionPicker>
            <PositionLabel>
              X: {((segment.targetX || 0.5) * 100).toFixed(1)}% • Y:{' '}
              {((segment.targetY || 0.5) * 100).toFixed(1)}%
            </PositionLabel>
          </Section>
        )}
      </EditorContent>
    </EditorPanel>
  );
};

export default ZoomEditor;

import { useState } from 'react';
import { PresetCelebrities } from './PresetCelebrities';
import { CustomCelebrity } from './CustomCelebrity';
import type { CelebrityConfig } from '../../types/media';

interface CelebrityConfigPanelProps {
  config: CelebrityConfig;
  onChange: (config: CelebrityConfig) => void;
}

export const CelebrityConfigPanel = ({ config, onChange }: CelebrityConfigPanelProps) => {
  const [mode, setMode] = useState<'preset' | 'custom'>(config.mode);

  const handleModeChange = (newMode: 'preset' | 'custom') => {
    setMode(newMode);
    if (newMode === 'preset') {
      onChange({ mode: 'preset', name: 'drake' });
    } else {
      onChange({ mode: 'custom', photoId: undefined, audioId: undefined });
    }
  };

  const handlePresetSelect = (name: string) => {
    onChange({ mode: 'preset', name });
  };

  const handlePhotoUpload = (photoId: string) => {
    onChange({ ...config, mode: 'custom', photoId });
  };

  const handleAudioUpload = (audioId: string) => {
    onChange({ ...config, mode: 'custom', audioId });
  };

  const handlePromptChange = (prompt: string) => {
    onChange({ ...config, nanoBananaPrompt: prompt });
  };

  return (
    <div className="celebrity-config-panel">
      <div className="mode-tabs">
        <button
          className={`mode-tab ${mode === 'preset' ? 'active' : ''}`}
          onClick={() => handleModeChange('preset')}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"
            />
          </svg>
          Preset Celebrities
        </button>
        <button
          className={`mode-tab ${mode === 'custom' ? 'active' : ''}`}
          onClick={() => handleModeChange('custom')}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
          Custom Upload
        </button>
      </div>

      <div className="config-content">
        {mode === 'preset' ? (
          <PresetCelebrities
            selected={config.name}
            onSelect={handlePresetSelect}
            nanoBananaPrompt={config.nanoBananaPrompt}
            onPromptChange={handlePromptChange}
          />
        ) : (
          <>
            <CustomCelebrity
              photoId={config.photoId}
              audioId={config.audioId}
              onPhotoUpload={handlePhotoUpload}
              onAudioUpload={handleAudioUpload}
            />

            {/* AI Image Customization for Custom Upload */}
            <div className="nano-banana-prompt-section">
              <label htmlFor="nano-banana-prompt-custom" className="prompt-label">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  width="18"
                  height="18"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01"
                  />
                </svg>
                AI Image Customization (Optional)
              </label>
              <p className="prompt-description">
                Transform this character's appearance with AI. Example: "wearing a lab coat and glasses", "in medieval armor", "as a superhero"
              </p>
              <textarea
                id="nano-banana-prompt-custom"
                className="nano-banana-prompt-input"
                placeholder="Describe how you want to customize this character's image..."
                value={config.nanoBananaPrompt || ''}
                onChange={(e) => handlePromptChange(e.target.value)}
                rows={3}
              />
            </div>
          </>
        )}
      </div>
    </div>
  );
};

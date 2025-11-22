import { useState } from 'react';
import { CelebrityConfigPanel } from './CelebrityConfigPanel';
import type { CelebrityConfig } from '../../types/media';

interface CelebritySelectorProps {
  celebrities: CelebrityConfig[];
  onCelebritiesChange: (celebrities: CelebrityConfig[]) => void;
}

export const CelebritySelector = ({ celebrities, onCelebritiesChange }: CelebritySelectorProps) => {
  const [selectedIndex, setSelectedIndex] = useState(0);

  const addCelebrity = () => {
    if (celebrities.length < 5) {
      onCelebritiesChange([
        ...celebrities,
        { mode: 'preset', name: 'drake' }
      ]);
      setSelectedIndex(celebrities.length);
    }
  };

  const removeCelebrity = (index: number) => {
    if (celebrities.length > 2) {
      const newCelebrities = celebrities.filter((_, i) => i !== index);
      onCelebritiesChange(newCelebrities);
      setSelectedIndex(Math.min(selectedIndex, newCelebrities.length - 1));
    }
  };

  const updateCelebrity = (index: number, config: CelebrityConfig) => {
    const newCelebrities = [...celebrities];
    newCelebrities[index] = config;
    onCelebritiesChange(newCelebrities);
  };

  return (
    <div className="celebrity-selector">
      <div className="selector-header">
        <h2 className="selector-title">Select Characters ({celebrities.length})</h2>
        <p className="selector-description">
          Choose 2-5 celebrities for your video
        </p>
      </div>

      <div className="celebrity-tabs">
        {celebrities.map((_, index) => (
          <div
            key={index}
            className={`celebrity-tab ${selectedIndex === index ? 'active' : ''}`}
            onClick={() => setSelectedIndex(index)}
          >
            <span>Character {index + 1}</span>
            {celebrities.length > 2 && (
              <button
                className="remove-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  removeCelebrity(index);
                }}
                aria-label={`Remove character ${index + 1}`}
              >
                ×
              </button>
            )}
          </div>
        ))}

        {celebrities.length < 5 && (
          <button className="add-celebrity-btn" onClick={addCelebrity}>
            + Add Character
          </button>
        )}
      </div>

      <div className="celebrity-config">
        <CelebrityConfigPanel
          config={celebrities[selectedIndex]}
          onChange={(config) => updateCelebrity(selectedIndex, config)}
        />
      </div>
    </div>
  );
};

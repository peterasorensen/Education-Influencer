import { useState, useEffect } from 'react';
import type { FollowUpQuestion } from '../../types/followup';

interface Props {
  question: FollowUpQuestion;
  value?: boolean;
  onChange: (value: boolean) => void;
}

export const ToggleQuestion: React.FC<Props> = ({ value, onChange }) => {
  const [isEnabled, setIsEnabled] = useState<boolean>(value ?? false);

  useEffect(() => {
    setIsEnabled(value ?? false);
  }, [value]);

  const handleToggle = () => {
    const newValue = !isEnabled;
    setIsEnabled(newValue);
    onChange(newValue);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleToggle();
    }
  };

  return (
    <div className="question-type toggle">
      <div className="toggle-container">
        <div className="toggle-labels">
          <span className={`toggle-option ${!isEnabled ? 'active' : ''}`}>No</span>
          <div
            className={`toggle-switch ${isEnabled ? 'active' : ''}`}
            onClick={handleToggle}
            onKeyDown={handleKeyDown}
            tabIndex={0}
            role="switch"
            aria-checked={isEnabled}
          >
            <div className="toggle-slider"></div>
          </div>
          <span className={`toggle-option ${isEnabled ? 'active' : ''}`}>Yes</span>
        </div>
        <div className="toggle-state">
          {isEnabled ? 'Enabled' : 'Disabled'}
        </div>
      </div>
    </div>
  );
};

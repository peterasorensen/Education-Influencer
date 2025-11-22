import { useState, useEffect } from 'react';
import type { FollowUpQuestion } from '../../types/followup';

interface Props {
  question: FollowUpQuestion;
  value?: string[];
  onChange: (value: string[]) => void;
}

export const MultiSelectQuestion: React.FC<Props> = ({ question, value, onChange }) => {
  const [selectedOptions, setSelectedOptions] = useState<string[]>(value || []);

  useEffect(() => {
    setSelectedOptions(value || []);
  }, [value]);

  const handleToggle = (option: string) => {
    const newSelected = selectedOptions.includes(option)
      ? selectedOptions.filter((o) => o !== option)
      : [...selectedOptions, option];

    setSelectedOptions(newSelected);
    onChange(newSelected);
  };

  const handleKeyDown = (e: React.KeyboardEvent, option: string) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleToggle(option);
    }
  };

  return (
    <div className="question-type multi-select">
      <div className="selected-count">
        {selectedOptions.length} selected
      </div>
      <div className="options-list">
        {question.options?.map((option) => {
          const isSelected = selectedOptions.includes(option);
          return (
            <div
              key={option}
              className={`option ${isSelected ? 'selected' : ''}`}
              onClick={() => handleToggle(option)}
              onKeyDown={(e) => handleKeyDown(e, option)}
              tabIndex={0}
              role="checkbox"
              aria-checked={isSelected}
            >
              <div className="option-checkbox">
                <div className={`checkbox-box ${isSelected ? 'checked' : ''}`}>
                  {isSelected && (
                    <svg
                      className="checkbox-check"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                    >
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  )}
                </div>
              </div>
              <div className="option-label">{option}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

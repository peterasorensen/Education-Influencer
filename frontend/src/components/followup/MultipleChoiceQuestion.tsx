import { useState, useEffect } from 'react';
import type { FollowUpQuestion } from '../../types/followup';

interface Props {
  question: FollowUpQuestion;
  value?: string;
  onChange: (value: string) => void;
}

export const MultipleChoiceQuestion: React.FC<Props> = ({ question, value, onChange }) => {
  const [selectedOption, setSelectedOption] = useState<string | undefined>(value);

  useEffect(() => {
    setSelectedOption(value);
  }, [value]);

  const handleSelect = (option: string) => {
    setSelectedOption(option);
    onChange(option);
  };

  const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
    const options = question.options || [];

    if (e.key === 'ArrowDown' && index < options.length - 1) {
      e.preventDefault();
      const nextOption = options[index + 1];
      handleSelect(nextOption);
      // Focus next element
      const nextElement = document.getElementById(`option-${question.id}-${index + 1}`);
      nextElement?.focus();
    } else if (e.key === 'ArrowUp' && index > 0) {
      e.preventDefault();
      const prevOption = options[index - 1];
      handleSelect(prevOption);
      // Focus previous element
      const prevElement = document.getElementById(`option-${question.id}-${index - 1}`);
      prevElement?.focus();
    } else if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleSelect(options[index]);
    }
  };

  return (
    <div className="question-type multiple-choice">
      <div className="options-list">
        {question.options?.map((option, index) => (
          <div
            key={option}
            id={`option-${question.id}-${index}`}
            className={`option ${selectedOption === option ? 'selected' : ''}`}
            onClick={() => handleSelect(option)}
            onKeyDown={(e) => handleKeyDown(e, index)}
            tabIndex={0}
            role="radio"
            aria-checked={selectedOption === option}
          >
            <div className="option-radio">
              <div className={`radio-circle ${selectedOption === option ? 'checked' : ''}`}>
                {selectedOption === option && <div className="radio-dot"></div>}
              </div>
            </div>
            <div className="option-label">{option}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

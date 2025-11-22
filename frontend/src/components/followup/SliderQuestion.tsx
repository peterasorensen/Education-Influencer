import { useState, useEffect } from 'react';
import type { FollowUpQuestion } from '../../types/followup';

interface Props {
  question: FollowUpQuestion;
  value?: number;
  onChange: (value: number) => void;
}

export const SliderQuestion: React.FC<Props> = ({ question, value, onChange }) => {
  const minValue = question.min_value ?? 1;
  const maxValue = question.max_value ?? 5;
  const [currentValue, setCurrentValue] = useState<number>(
    value ?? question.default_value ?? Math.floor((minValue + maxValue) / 2)
  );

  useEffect(() => {
    setCurrentValue(value ?? question.default_value ?? Math.floor((minValue + maxValue) / 2));
  }, [value, question.default_value, minValue, maxValue]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = parseInt(e.target.value, 10);
    setCurrentValue(newValue);
    onChange(newValue);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowLeft' || e.key === 'ArrowDown') {
      e.preventDefault();
      if (currentValue > minValue) {
        const newValue = currentValue - 1;
        setCurrentValue(newValue);
        onChange(newValue);
      }
    } else if (e.key === 'ArrowRight' || e.key === 'ArrowUp') {
      e.preventDefault();
      if (currentValue < maxValue) {
        const newValue = currentValue + 1;
        setCurrentValue(newValue);
        onChange(newValue);
      }
    }
  };

  const percentage = ((currentValue - minValue) / (maxValue - minValue)) * 100;

  return (
    <div className="question-type slider">
      <div className="slider-container">
        <div className="slider-header">
          <span className="slider-label">Value: {currentValue}</span>
        </div>
        <div className="slider-wrapper">
          <input
            type="range"
            className="slider"
            min={minValue}
            max={maxValue}
            value={currentValue}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            aria-valuemin={minValue}
            aria-valuemax={maxValue}
            aria-valuenow={currentValue}
          />
          <div
            className="slider-fill"
            style={{ width: `${percentage}%` }}
          ></div>
        </div>
        <div className="slider-labels">
          <span className="slider-min">{minValue}</span>
          <span className="slider-max">{maxValue}</span>
        </div>
      </div>
    </div>
  );
};

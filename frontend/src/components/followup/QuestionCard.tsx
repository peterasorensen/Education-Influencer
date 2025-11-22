import { MultipleChoiceQuestion } from './MultipleChoiceQuestion';
import { MultiSelectQuestion } from './MultiSelectQuestion';
import { ToggleQuestion } from './ToggleQuestion';
import { SliderQuestion } from './SliderQuestion';
import type { FollowUpQuestion } from '../../types/followup';
import { QuestionType } from '../../types/followup';

interface Props {
  question: FollowUpQuestion;
  answer?: any;
  onAnswer: (value: any) => void;
}

export const QuestionCard: React.FC<Props> = ({ question, answer, onAnswer }) => {
  const renderQuestion = () => {
    switch (question.question_type) {
      case QuestionType.MULTIPLE_CHOICE:
        return (
          <MultipleChoiceQuestion
            question={question}
            value={answer}
            onChange={onAnswer}
          />
        );
      case QuestionType.MULTI_SELECT:
        return (
          <MultiSelectQuestion
            question={question}
            value={answer}
            onChange={onAnswer}
          />
        );
      case QuestionType.TOGGLE:
        return (
          <ToggleQuestion
            question={question}
            value={answer}
            onChange={onAnswer}
          />
        );
      case QuestionType.SLIDER:
        return (
          <SliderQuestion
            question={question}
            value={answer}
            onChange={onAnswer}
          />
        );
      case QuestionType.SHORT_TEXT:
        return (
          <div className="question-type short-text">
            <input
              type="text"
              className="text-input"
              value={answer || ''}
              onChange={(e) => onAnswer(e.target.value)}
              placeholder="Type your answer..."
            />
          </div>
        );
      default:
        return <div>Unsupported question type</div>;
    }
  };

  return (
    <div className="question-card">
      <div className="question-header">
        <span className="question-category">{question.category}</span>
        {question.is_required && <span className="required-badge">Required</span>}
      </div>
      <h3 className="question-text">{question.question_text}</h3>
      <div className="question-content">
        {renderQuestion()}
      </div>
    </div>
  );
};

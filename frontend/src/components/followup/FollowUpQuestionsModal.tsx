import { useState, useEffect } from 'react';
import { QuestionCard } from './QuestionCard';
import { generateQuestions, refinePrompt } from '../../services/followupApi';
import type { FollowUpQuestion } from '../../types/followup';

interface Props {
  topic: string;
  onComplete: (refinedPrompt: string, context: any) => void;
  onSkip: () => void;
  isOpen: boolean;
}

export const FollowUpQuestionsModal: React.FC<Props> = ({
  topic,
  onComplete,
  onSkip,
  isOpen,
}) => {
  const [questions, setQuestions] = useState<FollowUpQuestion[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, any>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && topic) {
      fetchQuestions();
    }
  }, [isOpen, topic]);

  const fetchQuestions = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await generateQuestions(topic, 4);
      setQuestions(response.questions);

      // Initialize answers with default values
      const defaultAnswers: Record<string, any> = {};
      response.questions.forEach((q) => {
        if (q.default_value !== undefined) {
          defaultAnswers[q.id] = q.default_value;
        }
      });
      setAnswers(defaultAnswers);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate questions');
    } finally {
      setIsLoading(false);
    }
  };

  const handleNext = async () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else {
      // Submit answers and refine prompt
      await handleSubmit();
    }
  };

  const handleBack = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setError(null);

    try {
      const response = await refinePrompt(topic, questions, answers);
      onComplete(response.refined_prompt, response.context);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to refine prompt');
      setIsSubmitting(false);
    }
  };

  const handleAnswer = (value: any) => {
    const currentQuestion = questions[currentQuestionIndex];
    setAnswers({ ...answers, [currentQuestion.id]: value });
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onSkip();
    }
  };

  const isCurrentQuestionAnswered = () => {
    const currentQuestion = questions[currentQuestionIndex];
    if (!currentQuestion) return false;

    const answer = answers[currentQuestion.id];

    // Check if required question is answered
    if (currentQuestion.is_required) {
      if (answer === undefined || answer === null || answer === '') {
        return false;
      }
      // For multi-select, check if at least one option is selected
      if (Array.isArray(answer) && answer.length === 0) {
        return false;
      }
    }

    return true;
  };

  if (!isOpen) return null;

  return (
    <div className="modal active" onKeyDown={handleKeyDown}>
      <div className="modal-backdrop" onClick={onSkip}></div>
      <div className="modal-content followup-modal">
        <button className="modal-close" onClick={onSkip} aria-label="Close">
          <svg viewBox="0 0 20 20" fill="currentColor">
            <path
              fillRule="evenodd"
              d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
              clipRule="evenodd"
            />
          </svg>
        </button>

        <h2 className="modal-title">Let's Refine Your Video</h2>
        <p className="modal-subtitle">Answer a few quick questions for better results</p>

        {isLoading ? (
          <div className="loading-state">
            <div className="loading-spinner">
              <div className="spinner"></div>
            </div>
            <p className="loading-text">Generating personalized questions...</p>
          </div>
        ) : error ? (
          <div className="error-state">
            <svg className="error-icon" viewBox="0 0 20 20" fill="currentColor">
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
            <p className="error-text">{error}</p>
            <div className="error-actions">
              <button onClick={fetchQuestions} className="retry-button">
                Try Again
              </button>
              <button onClick={onSkip} className="skip-error-button">
                Skip & Generate
              </button>
            </div>
          </div>
        ) : questions.length > 0 ? (
          <>
            <div className="progress-indicator">
              <div className="progress-bar-container">
                <div
                  className="progress-bar-fill"
                  style={{
                    width: `${((currentQuestionIndex + 1) / questions.length) * 100}%`,
                  }}
                ></div>
              </div>
              <div className="progress-text">
                Question {currentQuestionIndex + 1} of {questions.length}
              </div>
            </div>

            <QuestionCard
              question={questions[currentQuestionIndex]}
              answer={answers[questions[currentQuestionIndex]?.id]}
              onAnswer={handleAnswer}
            />

            <div className="modal-actions">
              <button onClick={onSkip} className="skip-button">
                Skip All & Generate
              </button>
              <div className="navigation-buttons">
                {currentQuestionIndex > 0 && (
                  <button onClick={handleBack} className="back-button">
                    Back
                  </button>
                )}
                <button
                  onClick={handleNext}
                  className="next-button"
                  disabled={!isCurrentQuestionAnswered() || isSubmitting}
                >
                  {isSubmitting ? (
                    <>
                      <span className="spinner small"></span>
                      Refining...
                    </>
                  ) : currentQuestionIndex === questions.length - 1 ? (
                    'Generate Video'
                  ) : (
                    'Next'
                  )}
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="empty-state">
            <p>No questions available for this topic.</p>
            <button onClick={onSkip} className="skip-button">
              Continue Without Questions
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

// Follow-up Questions API Service

import type {
  FollowUpQuestion,
  QuestionGenerationResponse,
  PromptRefinementResponse,
} from '../types/followup';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Generate follow-up questions for a given topic
 */
export const generateQuestions = async (
  topic: string,
  maxQuestions?: number
): Promise<QuestionGenerationResponse> => {
  const response = await fetch(`${API_URL}/api/generate-questions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      topic,
      max_questions: maxQuestions || 4,
    }),
  });

  if (!response.ok) {
    throw new Error(`Failed to generate questions: ${response.status}`);
  }

  return response.json();
};

/**
 * Refine the original prompt based on user answers
 */
export const refinePrompt = async (
  originalTopic: string,
  questions: FollowUpQuestion[],
  answers: Record<string, any>
): Promise<PromptRefinementResponse> => {
  const response = await fetch(`${API_URL}/api/refine-prompt`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      original_topic: originalTopic,
      questions,
      answers,
    }),
  });

  if (!response.ok) {
    throw new Error(`Failed to refine prompt: ${response.status}`);
  }

  return response.json();
};

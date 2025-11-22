// Follow-up Questions Types

export const QuestionType = {
  MULTIPLE_CHOICE: "multiple_choice",
  MULTI_SELECT: "multi_select",
  SHORT_TEXT: "short_text",
  TOGGLE: "toggle",
  SLIDER: "slider"
} as const;

export type QuestionType = typeof QuestionType[keyof typeof QuestionType];

export interface FollowUpQuestion {
  id: string;
  question_text: string;
  question_type: QuestionType;
  category: string;
  options?: string[];
  default_value?: any;
  min_value?: number;
  max_value?: number;
  is_required: boolean;
}

export interface QuestionGenerationResponse {
  questions: FollowUpQuestion[];
  estimated_time_seconds: number;
}

export interface PromptRefinementResponse {
  refined_prompt: string;
  context: Record<string, any>;
}

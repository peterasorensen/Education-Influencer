import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { toast } from 'sonner';

const topicSchema = z.object({
  topic: z.string()
    .min(10, 'Topic must be at least 10 characters')
    .max(500, 'Topic must be less than 500 characters')
    .regex(/\w+/, 'Topic must contain at least one word')
});

type TopicFormData = z.infer<typeof topicSchema>;

interface TopicInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: (topic: string) => void;
  disabled?: boolean;
  resumeMode?: boolean;
}

export const TopicInput = ({ value, onChange, onSubmit, disabled = false, resumeMode = false }: TopicInputProps) => {
  const { register, handleSubmit, formState: { errors }, setValue } = useForm<TopicFormData>({
    resolver: zodResolver(topicSchema),
    mode: 'onChange',
    defaultValues: { topic: value }
  });

  // Sync external value changes with form
  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    onChange(newValue);
    setValue('topic', newValue, { shouldValidate: true });
  };

  const onFormSubmit = (data: TopicFormData) => {
    if (resumeMode) {
      // Skip validation in resume mode
      onSubmit(data.topic);
      return;
    }

    if (errors.topic) {
      toast.error(errors.topic.message || 'Invalid topic');
      return;
    }

    onSubmit(data.topic);
  };

  return (
    <form onSubmit={handleSubmit(onFormSubmit)} className="input-section">
      <div className="input-wrapper">
        <textarea
          {...register('topic')}
          className={`topic-input ${errors.topic ? 'error' : ''}`}
          value={value}
          onChange={handleChange}
          placeholder={resumeMode ? "Resuming from previous job..." : "Enter your educational topic... (e.g., 'Explain quantum entanglement', 'How does photosynthesis work?')"}
          disabled={disabled || resumeMode}
          rows={3}
          aria-label="Enter educational topic"
          aria-invalid={!!errors.topic}
          aria-describedby={errors.topic ? 'topic-error' : undefined}
        />
        {errors.topic && !resumeMode && (
          <span id="topic-error" className="input-error" role="alert">
            {errors.topic.message}
          </span>
        )}
      </div>
    </form>
  );
};

export default TopicInput;

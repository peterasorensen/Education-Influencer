import type { ConnectionState, PipelineStep, ProgressUpdate, StepInfo } from '../types';

const PIPELINE_STEPS: StepInfo[] = [
  {
    key: 'generating_script',
    label: 'Generating Script',
    description: 'AI is creating the educational script',
  },
  {
    key: 'creating_audio',
    label: 'Creating Audio',
    description: 'Converting script to natural speech',
  },
  {
    key: 'extracting_timestamps',
    label: 'Extracting Timestamps',
    description: 'Analyzing audio for timing',
  },
  {
    key: 'planning_visuals',
    label: 'Planning Visuals',
    description: 'Designing animation sequences',
  },
  {
    key: 'generating_animations',
    label: 'Generating Animations',
    description: 'Creating visual content (9:16 format)',
  },
  {
    key: 'creating_celebrity_videos',
    label: 'Creating Celebrity Video',
    description: 'Generating expressive celebrity narrator',
  },
  {
    key: 'lip_syncing',
    label: 'Lip-Syncing',
    description: 'Synchronizing audio with celebrity video',
  },
  {
    key: 'compositing_video',
    label: 'Compositing Video',
    description: 'Combining education & celebrity into 9:16 video',
  },
];

interface ProgressTrackerProps {
  connectionStatus: ConnectionState;
  steps: Map<PipelineStep, ProgressUpdate>;
  currentProgress?: number;
}

export const ProgressTracker = ({ connectionStatus, steps }: ProgressTrackerProps) => {
  const getStepStatus = (stepKey: PipelineStep): 'pending' | 'in_progress' | 'completed' | 'error' => {
    const update = steps.get(stepKey);
    return update?.status || 'pending';
  };

  return (
    <div className="progress-section" role="region" aria-label="Video generation progress">
      <div className="connection-status">
        <div className={`status-indicator ${connectionStatus}`} role="status" aria-live="polite"></div>
        <span className="status-text">
          {connectionStatus === 'connected' && 'Connected'}
          {connectionStatus === 'connecting' && 'Connecting...'}
          {connectionStatus === 'disconnected' && 'Disconnected'}
          {connectionStatus === 'error' && 'Connection Error'}
        </span>
      </div>

      <div className="steps-container">
        {PIPELINE_STEPS.map((step, index) => {
          const status = getStepStatus(step.key);
          const update = steps.get(step.key);

          return (
            <div
              key={step.key}
              className={`step-item ${status}`}
              role="listitem"
              aria-label={`${step.label} - ${status}`}
            >
              <div className="step-indicator">
                <div className="step-number" aria-hidden="true">{index + 1}</div>
                {status === 'in_progress' && (
                  <div className="step-spinner" aria-label="Processing"></div>
                )}
                {status === 'completed' && (
                  <svg
                    className="step-check"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                    aria-label="Completed"
                  >
                    <path
                      fillRule="evenodd"
                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                )}
                {status === 'error' && (
                  <svg
                    className="step-error"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                    aria-label="Error"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                      clipRule="evenodd"
                    />
                  </svg>
                )}
              </div>
              <div className="step-content">
                <h3 className="step-label">{step.label}</h3>
                <p className="step-description">
                  {update?.message || step.description}
                </p>
                {update?.progress !== undefined && (
                  <div
                    className="progress-bar"
                    role="progressbar"
                    aria-valuenow={update.progress}
                    aria-valuemin={0}
                    aria-valuemax={100}
                    aria-label={`${step.label} progress`}
                  >
                    <div
                      className="progress-fill"
                      style={{ width: `${update.progress}%` }}
                    ></div>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ProgressTracker;

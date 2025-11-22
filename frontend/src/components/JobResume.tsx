interface JobResumeProps {
  enabled: boolean;
  jobId: string;
  onToggle: (enabled: boolean) => void;
  onJobIdChange: (jobId: string) => void;
  lastJobId: string | null;
  disabled?: boolean;
}

export const JobResume = ({
  enabled,
  jobId,
  onToggle,
  onJobIdChange,
  lastJobId,
  disabled = false
}: JobResumeProps) => {
  return (
    <div className="resume-section">
      <label className="resume-checkbox">
        <input
          type="checkbox"
          checked={enabled}
          onChange={(e) => onToggle(e.target.checked)}
          disabled={disabled}
          aria-label="Resume from existing job"
        />
        <span className="resume-label">
          Resume from existing job
        </span>
      </label>
      {enabled && (
        <div className="manual-job-input">
          <input
            type="text"
            className="job-id-input"
            value={jobId}
            onChange={(e) => onJobIdChange(e.target.value)}
            placeholder={lastJobId ? `Last job: ${lastJobId}` : "Enter job ID (e.g., 550e8400-e29b-41d4...)"}
            disabled={disabled}
            aria-label="Job ID to resume"
            aria-describedby="job-id-hint"
          />
          <span id="job-id-hint" className="input-hint">
            Enter a job ID to resume a previous video generation
          </span>
        </div>
      )}
    </div>
  );
};

export default JobResume;

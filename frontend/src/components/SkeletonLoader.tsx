export const ProgressSkeleton = () => (
  <div className="skeleton-progress" role="status" aria-label="Loading progress">
    <div className="skeleton-line"></div>
    <div className="skeleton-line short"></div>
    <div className="skeleton-steps">
      {[...Array(8)].map((_, i) => (
        <div key={i} className="skeleton-step">
          <div className="skeleton-circle"></div>
          <div className="skeleton-content">
            <div className="skeleton-line"></div>
            <div className="skeleton-line short"></div>
          </div>
        </div>
      ))}
    </div>
    <span className="sr-only">Loading video generation progress...</span>
  </div>
);

export const VideoSkeleton = () => (
  <div className="skeleton-video" role="status" aria-label="Loading video">
    <div className="skeleton-video-player"></div>
    <div className="skeleton-actions">
      <div className="skeleton-button"></div>
      <div className="skeleton-button"></div>
    </div>
    <span className="sr-only">Loading video player...</span>
  </div>
);

export const InputSkeleton = () => (
  <div className="skeleton-input" role="status" aria-label="Loading form">
    <div className="skeleton-textarea"></div>
    <div className="skeleton-button wide"></div>
    <span className="sr-only">Loading input form...</span>
  </div>
);

export default ProgressSkeleton;

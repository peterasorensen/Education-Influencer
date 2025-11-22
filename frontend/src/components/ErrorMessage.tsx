interface ErrorMessageProps {
  error: string;
  onDismiss?: () => void;
}

const errorMessages: Record<string, { title: string; message: string; action?: string }> = {
  'connection_failed': {
    title: 'Connection Failed',
    message: 'Unable to connect to server. Please check your internet connection and try again.',
    action: 'Retry Connection'
  },
  'timeout': {
    title: 'Request Timed Out',
    message: 'The request took too long to complete. Please try again.',
    action: 'Try Again'
  },
  'invalid_topic': {
    title: 'Invalid Topic',
    message: 'Please enter a valid topic (10-500 characters with at least one word).',
  },
  'generation_failed': {
    title: 'Video Generation Failed',
    message: 'Unable to generate video. Please try again or contact support if the issue persists.',
    action: 'Try Again'
  },
  'server_error': {
    title: 'Server Error',
    message: 'An unexpected server error occurred. Our team has been notified.',
    action: 'Try Again'
  },
  'websocket_error': {
    title: 'Connection Lost',
    message: 'Lost connection to server. Your video may still be processing.',
    action: 'Reconnect'
  },
  'job_not_found': {
    title: 'Job Not Found',
    message: 'The job ID you entered could not be found. Please check and try again.',
  },
  'invalid_job_id': {
    title: 'Invalid Job ID',
    message: 'The job ID format is invalid. Please enter a valid UUID.',
  },
};

const getErrorDetails = (error: string) => {
  // Try to match known error patterns
  const errorKey = Object.keys(errorMessages).find(key =>
    error.toLowerCase().includes(key.replace(/_/g, ' '))
  );

  if (errorKey) {
    return errorMessages[errorKey];
  }

  // Check for HTTP status errors
  if (error.includes('status: 4')) {
    return {
      title: 'Request Error',
      message: 'Invalid request. Please check your input and try again.',
    };
  }

  if (error.includes('status: 5')) {
    return errorMessages.server_error;
  }

  // Default error
  return {
    title: 'Error',
    message: error,
  };
};

export const ErrorMessage = ({ error, onDismiss }: ErrorMessageProps) => {
  const errorDetails = getErrorDetails(error);

  return (
    <div className="error-message" role="alert" aria-live="assertive">
      <svg className="error-icon" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
        <path
          fillRule="evenodd"
          d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
          clipRule="evenodd"
        />
      </svg>
      <div className="error-content">
        <strong className="error-title">{errorDetails.title}</strong>
        <p className="error-description">{errorDetails.message}</p>
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="error-dismiss"
          aria-label="Dismiss error"
        >
          <svg viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path
              fillRule="evenodd"
              d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
              clipRule="evenodd"
            />
          </svg>
        </button>
      )}
    </div>
  );
};

export default ErrorMessage;

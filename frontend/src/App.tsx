import { useState, useEffect, useRef } from 'react';
import './App.css';
import type {
  PipelineStep,
  ProgressUpdate,
  VideoGenerationRequest,
  VideoGenerationResponse,
  VideoGenerationComplete,
  ConnectionState,
  StepInfo,
} from './types';

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
    description: 'Creating visual content',
  },
  {
    key: 'stitching_video',
    label: 'Stitching Video',
    description: 'Combining audio and visuals',
  },
];

function App() {
  const [topic, setTopic] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [connectionState, setConnectionState] = useState<ConnectionState>('disconnected');
  const [progressSteps, setProgressSteps] = useState<Map<PipelineStep, ProgressUpdate>>(new Map());
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!topic.trim()) {
      setError('Please enter a topic');
      return;
    }

    setIsGenerating(true);
    setError(null);
    setVideoUrl(null);
    setProgressSteps(new Map());

    try {
      // Send POST request to backend
      const response = await fetch('http://localhost:8000/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic } as VideoGenerationRequest),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: VideoGenerationResponse = await response.json();

      // Connect to WebSocket for progress updates
      const wsUrl = data.websocketUrl || `ws://localhost:8000/ws/${data.jobId}`;
      connectWebSocket(wsUrl);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start video generation');
      setIsGenerating(false);
    }
  };

  const connectWebSocket = (url: string) => {
    setConnectionState('connecting');

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnectionState('connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === 'progress') {
          const update: ProgressUpdate = data.data;
          setProgressSteps((prev) => {
            const newMap = new Map(prev);
            newMap.set(update.step, update);
            return newMap;
          });
        } else if (data.type === 'complete') {
          const complete: VideoGenerationComplete = data.data;
          // Prepend backend URL to relative video path
          const fullVideoUrl = `http://localhost:8000${complete.videoUrl}`;
          setVideoUrl(fullVideoUrl);
          setIsGenerating(false);
          setConnectionState('disconnected');
        } else if (data.type === 'error') {
          setError(data.message || 'An error occurred during video generation');
          setIsGenerating(false);
          setConnectionState('error');
        }
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setError('Connection error. Please try again.');
      setConnectionState('error');
      setIsGenerating(false);
    };

    ws.onclose = () => {
      setConnectionState('disconnected');
      if (isGenerating) {
        setIsGenerating(false);
      }
    };
  };

  const getStepStatus = (stepKey: PipelineStep): 'pending' | 'in_progress' | 'completed' | 'error' => {
    const update = progressSteps.get(stepKey);
    return update?.status || 'pending';
  };

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1 className="title">EduVideo AI</h1>
          <p className="tagline">Transform any topic into an engaging educational video</p>
        </header>

        <main className="main-content">
          <form onSubmit={handleSubmit} className="input-section">
            <div className="input-wrapper">
              <textarea
                className="topic-input"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="Enter your educational topic... (e.g., 'Explain quantum entanglement', 'How does photosynthesis work?')"
                disabled={isGenerating}
                rows={3}
              />
            </div>
            <button
              type="submit"
              className={`generate-button ${isGenerating ? 'generating' : ''}`}
              disabled={isGenerating}
            >
              {isGenerating ? (
                <>
                  <span className="spinner"></span>
                  Generating...
                </>
              ) : (
                'Generate Video'
              )}
            </button>
          </form>

          {error && (
            <div className="error-message">
              <svg className="error-icon" viewBox="0 0 20 20" fill="currentColor">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
              {error}
            </div>
          )}

          {isGenerating && (
            <div className="progress-section">
              <div className="connection-status">
                <div className={`status-indicator ${connectionState}`}></div>
                <span className="status-text">
                  {connectionState === 'connected' && 'Connected'}
                  {connectionState === 'connecting' && 'Connecting...'}
                  {connectionState === 'disconnected' && 'Disconnected'}
                  {connectionState === 'error' && 'Connection Error'}
                </span>
              </div>

              <div className="steps-container">
                {PIPELINE_STEPS.map((step, index) => {
                  const status = getStepStatus(step.key);
                  const update = progressSteps.get(step.key);

                  return (
                    <div key={step.key} className={`step-item ${status}`}>
                      <div className="step-indicator">
                        <div className="step-number">{index + 1}</div>
                        {status === 'in_progress' && <div className="step-spinner"></div>}
                        {status === 'completed' && (
                          <svg className="step-check" viewBox="0 0 20 20" fill="currentColor">
                            <path
                              fillRule="evenodd"
                              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                              clipRule="evenodd"
                            />
                          </svg>
                        )}
                        {status === 'error' && (
                          <svg className="step-error" viewBox="0 0 20 20" fill="currentColor">
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
                          <div className="progress-bar">
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
          )}

          {videoUrl && (
            <div className="video-section">
              <h2 className="video-title">Your Video is Ready!</h2>
              <div className="video-wrapper">
                <video className="video-player" controls src={videoUrl}>
                  Your browser does not support the video tag.
                </video>
              </div>
              <div className="action-buttons">
                <a
                  href={videoUrl}
                  download
                  className="download-button"
                >
                  Download Video
                </a>
                <button
                  onClick={() => {
                    setVideoUrl(null);
                    setTopic('');
                    setProgressSteps(new Map());
                  }}
                  className="new-video-button"
                >
                  Create Another Video
                </button>
              </div>
            </div>
          )}
        </main>

        <footer className="footer">
          <p>Powered by AI • Create unlimited educational videos</p>
        </footer>
      </div>
    </div>
  );
}

export default App;

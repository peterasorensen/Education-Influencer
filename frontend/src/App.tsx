import { useState, useEffect, useRef } from 'react';
import { toast } from 'sonner';
import './App.css';
import type {
  PipelineStep,
  ProgressUpdate,
  VideoGenerationResponse,
  VideoGenerationComplete,
  ConnectionState,
} from './types';
import type { CelebrityConfig } from './types/media';

// Components
import Header from './components/Header';
import TopicInput from './components/TopicInput';
import RendererSelector from './components/RendererSelector';
import JobResume from './components/JobResume';
import ProgressTracker from './components/ProgressTracker';
import VideoPlayer from './components/VideoPlayer';
import ErrorMessage from './components/ErrorMessage';
import Toast from './components/Toast';
import { FollowUpQuestionsModal } from './components/followup/FollowUpQuestionsModal';
import { CelebritySelector } from './components/celebrity/CelebritySelector';

function App() {
  const [topic, setTopic] = useState('');
  const [renderer, setRenderer] = useState<'manim' | 'remotion'>('manim');
  const [isGenerating, setIsGenerating] = useState(false);
  const [connectionState, setConnectionState] = useState<ConnectionState>('disconnected');
  const [progressSteps, setProgressSteps] = useState<Map<PipelineStep, ProgressUpdate>>(new Map());
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lastJobId, setLastJobId] = useState<string | null>(localStorage.getItem('lastJobId'));
  const [manualJobId, setManualJobId] = useState('');
  const [resumeMode, setResumeMode] = useState(false);
  const [showFollowUpModal, setShowFollowUpModal] = useState(false);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [refinedPrompt, setRefinedPrompt] = useState<string | null>(null);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [refinedContext, setRefinedContext] = useState<any>(null);
  const [celebrities, setCelebrities] = useState<CelebrityConfig[]>([
    { mode: 'preset', name: 'drake' },
    { mode: 'preset', name: 'sydney_sweeney' }
  ]);
  const wsRef = useRef<WebSocket | null>(null);

  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const handleSubmit = async (submitTopic: string) => {
    if (!submitTopic.trim() && !resumeMode) {
      toast.error('Please enter a topic');
      setError('Please enter a topic');
      return;
    }

    const jobIdToResume = manualJobId.trim() || lastJobId;

    if (resumeMode && !jobIdToResume) {
      toast.error('Please enter a job ID to resume');
      setError('Please enter a job ID to resume');
      return;
    }

    // If in resume mode, skip follow-up questions
    if (resumeMode) {
      startVideoGeneration(submitTopic || 'Resuming...', null, jobIdToResume);
    } else {
      // Show follow-up questions modal
      setShowFollowUpModal(true);
    }
  };

  const handleFollowUpComplete = (refined: string, context: any) => {
    setRefinedPrompt(refined);
    setRefinedContext(context);
    setShowFollowUpModal(false);
    // Start video generation with refined prompt
    console.log('Follow-up refinement:', { refined, context });
    startVideoGeneration(refined, context, null);
  };

  const handleFollowUpSkip = () => {
    setShowFollowUpModal(false);
    // Start video generation with original topic
    startVideoGeneration(topic, null, null);
  };

  const startVideoGeneration = async (topicText: string, context: any, resumeJobId: string | null) => {
    setIsGenerating(true);
    setError(null);
    setVideoUrl(null);
    setProgressSteps(new Map());

    // Show loading toast
    const loadingToast = toast.loading(resumeJobId ? 'Resuming video generation...' : 'Starting video generation...');

    try {
      // Send POST request to backend
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

      const requestBody: any = resumeJobId
        ? { topic: topicText, resume_job_id: resumeJobId, renderer }
        : {
            topic: topicText,
            renderer,
            refined_context: context,
            celebrities
          };

      const response = await fetch(`${apiUrl}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: VideoGenerationResponse = await response.json();

      // Save job ID to localStorage
      setLastJobId(data.jobId);
      localStorage.setItem('lastJobId', data.jobId);

      // Disable resume mode after starting
      setResumeMode(false);

      // Dismiss loading toast and show success
      toast.dismiss(loadingToast);
      toast.success(resumeJobId ? 'Resuming video generation!' : 'Video generation started!', {
        description: `Job ID: ${data.jobId.substring(0, 8)}...`
      });

      // Connect to WebSocket for progress updates
      const wsBaseUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
      const wsUrl = data.websocketUrl || `${wsBaseUrl}/ws/${data.jobId}`;
      connectWebSocket(wsUrl);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to start video generation';
      setError(errorMessage);
      setIsGenerating(false);

      toast.dismiss(loadingToast);
      toast.error('Failed to start generation', {
        description: errorMessage
      });
    }
  };

  const connectWebSocket = (url: string, retryCount = 0) => {
    setConnectionState('connecting');
    if (retryCount === 0) {
      toast.info('Connecting to server...');
    }

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnectionState('connected');
      if (retryCount === 0) {
        toast.success('Connected to server');
      }
      console.log('WebSocket connected');
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

          // Show toast for step changes
          if (update.status === 'in_progress') {
            toast.info(update.message || `Processing: ${update.step.replace(/_/g, ' ')}`);
          } else if (update.status === 'completed') {
            toast.success(`Completed: ${update.step.replace(/_/g, ' ')}`);
          } else if (update.status === 'error') {
            toast.error(`Error in: ${update.step.replace(/_/g, ' ')}`);
          }
        } else if (data.type === 'complete') {
          const complete: VideoGenerationComplete = data.data;
          // Prepend backend URL to relative video path
          const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
          const fullVideoUrl = `${apiUrl}${complete.videoUrl}`;
          setVideoUrl(fullVideoUrl);
          setIsGenerating(false);
          setConnectionState('disconnected');

          toast.success('Video generated successfully!', {
            description: `Duration: ${complete.duration}s`,
            duration: 6000
          });
        } else if (data.type === 'error') {
          const errorMsg = data.message || 'An error occurred during video generation';
          setError(errorMsg);
          setIsGenerating(false);
          setConnectionState('error');

          toast.error('Generation failed', {
            description: errorMsg
          });
        } else if (data.type === 'ping') {
          // Respond to server pings to keep connection alive
          console.log('Received ping from server');
        }
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
        toast.error('Failed to parse server message');
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      if (retryCount === 0) {
        toast.error('WebSocket connection error');
      }
    };

    ws.onclose = (event) => {
      console.log('WebSocket closed:', event.code, event.reason);

      // If we're still generating and connection closed unexpectedly, try to reconnect
      if (isGenerating && retryCount < 3) {
        console.log(`Attempting to reconnect (attempt ${retryCount + 1}/3)...`);
        setConnectionState('connecting');
        toast.warning(`Reconnecting (${retryCount + 1}/3)...`);

        setTimeout(() => {
          connectWebSocket(url, retryCount + 1);
        }, 2000 * (retryCount + 1)); // Exponential backoff
      } else {
        setConnectionState('disconnected');
        if (isGenerating && retryCount >= 3) {
          const errorMsg = 'Lost connection to server. Your video may still be processing.';
          setError(errorMsg);
          setIsGenerating(false);

          toast.error('Connection lost', {
            description: 'Max retry attempts reached. Your video may still be processing.'
          });
        }
      }
    };
  };

  const handleNewVideo = () => {
    setVideoUrl(null);
    setTopic('');
    setProgressSteps(new Map());
    setResumeMode(false);
    setError(null);
    setRefinedPrompt(null);
    setRefinedContext(null);
    setCelebrities([
      { mode: 'preset', name: 'drake' },
      { mode: 'preset', name: 'sydney_sweeney' }
    ]);
    toast.info('Ready to create a new video');
  };

  const handleDismissError = () => {
    setError(null);
  };

  return (
    <div className="app">
      <Toast />
      <div className="container">
        <Header />

        <main className="main-content">
          <div>
            <TopicInput
              value={topic}
              onChange={setTopic}
              onSubmit={handleSubmit}
              disabled={isGenerating}
              resumeMode={resumeMode}
            />

            {!isGenerating && (
              <>
                <RendererSelector
                  value={renderer}
                  onChange={setRenderer}
                  disabled={isGenerating}
                />

                <JobResume
                  enabled={resumeMode}
                  jobId={manualJobId}
                  onToggle={setResumeMode}
                  onJobIdChange={setManualJobId}
                  lastJobId={lastJobId}
                  disabled={isGenerating}
                />
              </>
            )}

            {!isGenerating && !resumeMode && (
              <CelebritySelector
                celebrities={celebrities}
                onCelebritiesChange={setCelebrities}
              />
            )}

            <button
              type="submit"
              className={`generate-button ${isGenerating ? 'generating' : ''} ${resumeMode ? 'resume-mode' : ''}`}
              disabled={isGenerating}
              onClick={() => handleSubmit(topic)}
              aria-label={isGenerating ? 'Generating video' : resumeMode ? 'Resume and continue' : 'Generate video'}
              aria-busy={isGenerating}
            >
              {isGenerating ? (
                <>
                  <span className="spinner" aria-hidden="true"></span>
                  {resumeMode ? 'Resuming...' : 'Generating...'}
                </>
              ) : resumeMode ? (
                'Resume & Continue'
              ) : (
                'Generate Video'
              )}
            </button>
          </div>

          {error && (
            <ErrorMessage error={error} onDismiss={handleDismissError} />
          )}

          {isGenerating && (
            <ProgressTracker
              connectionStatus={connectionState}
              steps={progressSteps}
            />
          )}

          {videoUrl && (
            <VideoPlayer
              url={videoUrl}
              onNewVideo={handleNewVideo}
            />
          )}
        </main>

        <footer className="footer">
          <p>Powered by AI • Create unlimited educational videos</p>
        </footer>
      </div>

      <FollowUpQuestionsModal
        topic={topic}
        onComplete={handleFollowUpComplete}
        onSkip={handleFollowUpSkip}
        isOpen={showFollowUpModal}
      />
    </div>
  );
}

export default App;

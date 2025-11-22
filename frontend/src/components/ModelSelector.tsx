interface ModelSelectorProps {
  scriptModel: 'gpt-4o' | 'gpt-4o-mini' | 'gpt-3.5-turbo';
  audioModel: 'openai-tts' | 'tortoise-tts' | 'minimax-voice-cloning';
  videoModel: 'seedance' | 'kling-turbo';
  lipsyncModel: 'tmappdev' | 'kling' | 'pixverse';
  onScriptModelChange: (value: 'gpt-4o' | 'gpt-4o-mini' | 'gpt-3.5-turbo') => void;
  onAudioModelChange: (value: 'openai-tts' | 'tortoise-tts' | 'minimax-voice-cloning') => void;
  onVideoModelChange: (value: 'seedance' | 'kling-turbo') => void;
  onLipsyncModelChange: (value: 'tmappdev' | 'kling' | 'pixverse') => void;
  disabled?: boolean;
}

export const ModelSelector = ({
  scriptModel,
  audioModel,
  videoModel,
  lipsyncModel,
  onScriptModelChange,
  onAudioModelChange,
  onVideoModelChange,
  onLipsyncModelChange,
  disabled = false
}: ModelSelectorProps) => {
  return (
    <div className="model-selector-container">
      {/* Script Model Selection */}
      <div className="model-section">
        <label className="model-label">Script Generation:</label>
        <div className="model-options">
          <label className={`model-option ${scriptModel === 'gpt-4o' ? 'selected' : ''}`}>
            <input
              type="radio"
              name="script-model"
              value="gpt-4o"
              checked={scriptModel === 'gpt-4o'}
              onChange={(e) => onScriptModelChange(e.target.value as any)}
              disabled={disabled}
            />
            <span className="option-text">
              <strong>GPT-4o</strong>
              <span className="option-desc">Best quality • $$$</span>
            </span>
          </label>
          <label className={`model-option ${scriptModel === 'gpt-4o-mini' ? 'selected' : ''}`}>
            <input
              type="radio"
              name="script-model"
              value="gpt-4o-mini"
              checked={scriptModel === 'gpt-4o-mini'}
              onChange={(e) => onScriptModelChange(e.target.value as any)}
              disabled={disabled}
            />
            <span className="option-text">
              <strong>GPT-4o Mini</strong>
              <span className="option-desc">Good quality • $$</span>
            </span>
          </label>
          <label className={`model-option ${scriptModel === 'gpt-3.5-turbo' ? 'selected' : ''}`}>
            <input
              type="radio"
              name="script-model"
              value="gpt-3.5-turbo"
              checked={scriptModel === 'gpt-3.5-turbo'}
              onChange={(e) => onScriptModelChange(e.target.value as any)}
              disabled={disabled}
            />
            <span className="option-text">
              <strong>GPT-3.5 Turbo</strong>
              <span className="option-desc">Fastest • $</span>
            </span>
          </label>
        </div>
      </div>

      {/* Audio Model Selection */}
      <div className="model-section">
        <label className="model-label">Voice Generation:</label>
        <div className="model-options">
          <label className={`model-option ${audioModel === 'openai-tts' ? 'selected' : ''}`}>
            <input
              type="radio"
              name="audio-model"
              value="openai-tts"
              checked={audioModel === 'openai-tts'}
              onChange={(e) => onAudioModelChange(e.target.value as any)}
              disabled={disabled}
            />
            <span className="option-text">
              <strong>OpenAI TTS</strong>
              <span className="option-desc">Fast & Natural • $</span>
            </span>
          </label>
          <label className={`model-option ${audioModel === 'tortoise-tts' ? 'selected' : ''}`}>
            <input
              type="radio"
              name="audio-model"
              value="tortoise-tts"
              checked={audioModel === 'tortoise-tts'}
              onChange={(e) => onAudioModelChange(e.target.value as any)}
              disabled={disabled}
            />
            <span className="option-text">
              <strong>Tortoise TTS</strong>
              <span className="option-desc">Voice Cloning • $$</span>
            </span>
          </label>
          <label className={`model-option ${audioModel === 'minimax-voice-cloning' ? 'selected' : ''}`}>
            <input
              type="radio"
              name="audio-model"
              value="minimax-voice-cloning"
              checked={audioModel === 'minimax-voice-cloning'}
              onChange={(e) => onAudioModelChange(e.target.value as any)}
              disabled={disabled}
            />
            <span className="option-text">
              <strong>MiniMax Clone</strong>
              <span className="option-desc">HD Voice Cloning • $$$</span>
            </span>
          </label>
        </div>
      </div>

      {/* Video Model Selection */}
      <div className="model-section">
        <label className="model-label">Celebrity Video Generation:</label>
        <div className="model-options">
          <label className={`model-option ${videoModel === 'seedance' ? 'selected' : ''}`}>
            <input
              type="radio"
              name="video-model"
              value="seedance"
              checked={videoModel === 'seedance'}
              onChange={(e) => onVideoModelChange(e.target.value as any)}
              disabled={disabled}
            />
            <span className="option-text">
              <strong>SeeDance Pro</strong>
              <span className="option-desc">Fast & Reliable • $</span>
            </span>
          </label>
          <label className={`model-option ${videoModel === 'kling-turbo' ? 'selected' : ''}`}>
            <input
              type="radio"
              name="video-model"
              value="kling-turbo"
              checked={videoModel === 'kling-turbo'}
              onChange={(e) => onVideoModelChange(e.target.value as any)}
              disabled={disabled}
            />
            <span className="option-text">
              <strong>Kling v2.5 Turbo</strong>
              <span className="option-desc">High Quality • $$</span>
            </span>
          </label>
        </div>
      </div>

      {/* Lip Sync Model Selection */}
      <div className="model-section">
        <label className="model-label">Lip Sync:</label>
        <div className="model-options">
          <label className={`model-option ${lipsyncModel === 'tmappdev' ? 'selected' : ''}`}>
            <input
              type="radio"
              name="lipsync-model"
              value="tmappdev"
              checked={lipsyncModel === 'tmappdev'}
              onChange={(e) => onLipsyncModelChange(e.target.value as any)}
              disabled={disabled}
            />
            <span className="option-text">
              <strong>TmappDev</strong>
              <span className="option-desc">Most Reliable • $$</span>
            </span>
          </label>
          <label className={`model-option ${lipsyncModel === 'kling' ? 'selected' : ''}`}>
            <input
              type="radio"
              name="lipsync-model"
              value="kling"
              checked={lipsyncModel === 'kling'}
              onChange={(e) => onLipsyncModelChange(e.target.value as any)}
              disabled={disabled}
            />
            <span className="option-text">
              <strong>Kling</strong>
              <span className="option-desc">Budget Option • $</span>
            </span>
          </label>
          <label className={`model-option ${lipsyncModel === 'pixverse' ? 'selected' : ''}`}>
            <input
              type="radio"
              name="lipsync-model"
              value="pixverse"
              checked={lipsyncModel === 'pixverse'}
              onChange={(e) => onLipsyncModelChange(e.target.value as any)}
              disabled={disabled}
            />
            <span className="option-text">
              <strong>Pixverse</strong>
              <span className="option-desc">Alternative • $$</span>
            </span>
          </label>
        </div>
      </div>
    </div>
  );
};

export default ModelSelector;

interface RendererSelectorProps {
  value: 'manim' | 'remotion';
  onChange: (value: 'manim' | 'remotion') => void;
  disabled?: boolean;
}

export const RendererSelector = ({ value, onChange, disabled = false }: RendererSelectorProps) => {
  return (
    <div className="renderer-section">
      <label className="renderer-label">Animation Renderer:</label>
      <div className="renderer-options">
        <label
          className={`renderer-option ${value === 'manim' ? 'selected' : ''}`}
          aria-label="Select Manim renderer"
        >
          <input
            type="radio"
            name="renderer"
            value="manim"
            checked={value === 'manim'}
            onChange={(e) => onChange(e.target.value as 'manim' | 'remotion')}
            disabled={disabled}
            aria-checked={value === 'manim'}
          />
          <span className="option-text">
            <strong>Manim</strong>
            <span className="option-desc">Python • Math/Science • Traditional</span>
          </span>
        </label>
        <label
          className={`renderer-option ${value === 'remotion' ? 'selected' : ''}`}
          aria-label="Select Remotion renderer"
        >
          <input
            type="radio"
            name="renderer"
            value="remotion"
            checked={value === 'remotion'}
            onChange={(e) => onChange(e.target.value as 'manim' | 'remotion')}
            disabled={disabled}
            aria-checked={value === 'remotion'}
          />
          <span className="option-text">
            <strong>Remotion</strong>
            <span className="option-desc">React • Modern UI • GPU-Accelerated</span>
          </span>
        </label>
      </div>
    </div>
  );
};

export default RendererSelector;

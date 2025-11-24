"""
Remotion Generator Module

Generates Remotion (React/TypeScript) code from visual instructions with self-fixing capabilities.
Validates generated code and retries with error feedback up to 3 times.
"""

import logging
from typing import Callable, Optional, List, Dict, Tuple
from pathlib import Path
import asyncio
import subprocess
import re
from openai import AsyncOpenAI
import json
import shutil

logger = logging.getLogger(__name__)


class RemotionGenerator:
    """Generate and validate Remotion code with self-fixing loop."""

    MAX_RETRIES = 3

    def __init__(self, api_key: str):
        """
        Initialize the Remotion generator.

        Args:
            api_key: OpenAI API key
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "gpt-4o"

    async def generate_remotion_code(
        self,
        visual_instructions: List[Dict],
        topic: str,
        output_dir: Path,
        target_duration: float = 60.0,
        progress_callback: Optional[Callable[[str, int], None]] = None,
        script: Optional[List[Dict[str, str]]] = None,
    ) -> Path:
        """
        Generate Remotion code from visual instructions with self-fixing.

        Args:
            visual_instructions: List of visual instruction segments
            topic: Educational topic
            output_dir: Directory to save the generated Remotion project
            target_duration: Target duration in seconds
            progress_callback: Optional callback for progress updates

        Returns:
            Path to the generated and validated Remotion project directory

        Raises:
            Exception: If code generation fails after max retries
        """
        if progress_callback:
            progress_callback("Generating Remotion code...", 50)

        remotion_code = None
        last_error = None
        conversation_history = []

        for attempt in range(self.MAX_RETRIES):
            try:
                logger.info(f"Remotion code generation attempt {attempt + 1}/{self.MAX_RETRIES}")

                if progress_callback:
                    progress_callback(
                        f"Generating Remotion code (attempt {attempt + 1}/{self.MAX_RETRIES})...",
                        50 + (attempt * 3),
                    )

                # Generate code
                if attempt == 0:
                    remotion_code, conversation_history = await self._generate_initial_code(
                        visual_instructions, topic, target_duration, script
                    )
                else:
                    remotion_code, conversation_history = await self._fix_code(
                        remotion_code, last_error, conversation_history, attempt
                    )

                # Setup Remotion project structure
                await self._setup_remotion_project(output_dir, remotion_code)

                # Validate code (TypeScript/syntax check)
                is_valid, error_message = await self._validate_code(output_dir)

                if not is_valid:
                    logger.warning(
                        f"Validation failed (attempt {attempt + 1}): {error_message}"
                    )
                    # Log the generated code for debugging
                    root_file = output_dir / "src" / "Root.tsx"
                    if root_file.exists():
                        generated_code = root_file.read_text(encoding="utf-8")
                        logger.debug(f"Generated code (first 1000 chars):\n{generated_code[:1000]}")
                    last_error = f"Validation Error:\n{error_message}"
                    continue

                logger.info("Remotion code generated and validated successfully")
                if progress_callback:
                    progress_callback("Remotion code validated successfully", 59)
                return output_dir

            except Exception as e:
                import traceback
                error_traceback = traceback.format_exc()
                logger.error(f"Exception during attempt {attempt + 1}: {e}")
                logger.error(f"Traceback:\n{error_traceback}")
                last_error = f"Exception:\n{str(e)}\n\nTraceback:\n{error_traceback}"
                continue

        # Max retries exceeded
        error_msg = f"Failed to generate valid Remotion code after {self.MAX_RETRIES} attempts. Last error: {last_error}"
        logger.error(error_msg)
        raise Exception(error_msg)

    async def _generate_initial_code(
        self, visual_instructions: List[Dict], topic: str, target_duration: float = 60.0, script: Optional[List[Dict[str, str]]] = None
    ) -> Tuple[str, List[Dict]]:
        """Generate initial Remotion code from visual instructions.

        Returns:
            Tuple of (generated_code, conversation_history)
        """
        system_prompt = """Generate Remotion code for educational animations with DIAGRAMS, EQUATIONS, and ILLUSTRATIONS.

CANVAS: 1080x960 (9:8), 30fps. Safe area: 50px margins.

VISUAL TYPES - Render based on visual_type field:

1. EQUATIONS: Math formulas with <Equation> component
   - E = mc², x² + y² = r², F = ma, etc.
   - Variables in italic, proper subscripts/superscripts

2. DIAGRAMS: Flowcharts/process diagrams
   - <Box> for nodes with SHORT labels ("Input", "CPU", "Output")
   - <Arrow> to connect boxes
   - NO narration text - subtitles handle that!

3. GRAPHS: Coordinate plots
   - <GraphAxes> for x/y axes
   - <PlotCurve> for data
   - ONLY label axes ("x", "y", "t", etc.)

4. SHAPES: Geometric figures
   - <Shape> for circles, triangles, squares
   - Add measurements/angles ONLY ("90°", "5cm")

CRITICAL: NO NARRATION TEXT! Subtitles handle speech. Text is ONLY for:
- Math equations
- Short labels on diagrams
- Axis labels
- Measurements/annotations

TEMPLATE WITH VISUAL COMPONENT EXAMPLES:
```tsx
import React from 'react';
import { AbsoluteFill, Composition, useCurrentFrame, useVideoConfig, interpolate, spring, Easing, registerRoot } from 'remotion';

// EQUATION COMPONENT - For math formulas
const Equation: React.FC<{text: string; x: number; y: number; startFrame: number; endFrame: number; size?: number}> = ({text, x, y, startFrame, endFrame, size = 48}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const scale = spring({frame: frame - startFrame, fps, config: {damping: 15}});
  // Fade in at start, fade out at end
  const opacity = interpolate(
    frame,
    [startFrame, startFrame + 15, endFrame - 15, endFrame],
    [0, 1, 1, 0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}
  );

  return (
    <div style={{position: 'absolute', left: x, top: y, transform: `scale(${scale})`, opacity}}>
      <svg width={size * text.length * 0.6} height={size * 1.5}>
        <text x="50%" y="50%" fill="#00d4ff" fontSize={size} fontFamily="Georgia, serif" fontStyle="italic" textAnchor="middle" dominantBaseline="middle">
          {text}
        </text>
      </svg>
    </div>
  );
};

// ARROW COMPONENT - For diagrams
const Arrow: React.FC<{x1: number; y1: number; x2: number; y2: number; startFrame: number; color?: string}> = ({x1, y1, x2, y2, startFrame, color = '#00d4ff'}) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [startFrame, startFrame + 30], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});

  const currentX2 = x1 + (x2 - x1) * progress;
  const currentY2 = y1 + (y2 - y1) * progress;
  const angle = Math.atan2(y2 - y1, x2 - x1);

  return (
    <svg width={1080} height={960} style={{position: 'absolute', top: 0, left: 0}}>
      <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
          <polygon points="0 0, 10 3, 0 6" fill={color} />
        </marker>
      </defs>
      <line x1={x1} y1={y1} x2={currentX2} y2={currentY2} stroke={color} strokeWidth={3} markerEnd="url(#arrowhead)" />
    </svg>
  );
};

// DIAGRAM BOX - For flowcharts/diagrams
const Box: React.FC<{text: string; x: number; y: number; width: number; height: number; startFrame: number; color?: string}> = ({text, x, y, width, height, startFrame, color = '#00d4ff'}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const scale = spring({frame: frame - startFrame, fps, config: {damping: 12}});
  const opacity = interpolate(frame, [startFrame, startFrame + 20], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

  return (
    <div style={{position: 'absolute', left: x, top: y, transform: `scale(${scale})`, opacity}}>
      <svg width={width} height={height}>
        <rect x={2} y={2} width={width - 4} height={height - 4} fill="rgba(0, 212, 255, 0.1)" stroke={color} strokeWidth={3} rx={8} />
        <text x="50%" y="50%" fill="#fff" fontSize={20} fontFamily="Arial" textAnchor="middle" dominantBaseline="middle" fontWeight="600">
          {text}
        </text>
      </svg>
    </div>
  );
};

// GRAPH AXES - For plotting
const GraphAxes: React.FC<{startFrame: number}> = ({startFrame}) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [startFrame, startFrame + 40], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

  return (
    <svg width={1080} height={960} style={{position: 'absolute', top: 0, left: 0}}>
      {/* X-axis */}
      <line x1={150} y1={700} x2={150 + 700 * progress} y2={700} stroke="#888" strokeWidth={2} />
      {/* Y-axis */}
      <line x1={150} y1={700} x2={150} y2={700 - 500 * progress} stroke="#888" strokeWidth={2} />
      {/* Labels */}
      <text x={850} y={730} fill="#aaa" fontSize={18}>x</text>
      <text x={120} y={210} fill="#aaa" fontSize={18}>y</text>
    </svg>
  );
};

// PLOT CURVE - For function graphs
const PlotCurve: React.FC<{points: Array<{x: number; y: number}>; startFrame: number; color?: string}> = ({points, startFrame, color = '#00ff88'}) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [startFrame, startFrame + 60], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.ease)});

  const visiblePoints = points.slice(0, Math.floor(points.length * progress));
  const pathD = visiblePoints.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');

  return (
    <svg width={1080} height={960} style={{position: 'absolute', top: 0, left: 0}}>
      <path d={pathD} stroke={color} strokeWidth={3} fill="none" />
    </svg>
  );
};

// SHAPE - For geometry
const Shape: React.FC<{type: 'circle'|'triangle'|'square'; x: number; y: number; size: number; startFrame: number; color?: string}> = ({type, x, y, size, startFrame, color = '#ff00ff'}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const scale = spring({frame: frame - startFrame, fps, config: {damping: 10}});

  return (
    <div style={{position: 'absolute', left: x, top: y, transform: `scale(${scale})`}}>
      <svg width={size} height={size}>
        {type === 'circle' && <circle cx={size/2} cy={size/2} r={size/2 - 5} fill="none" stroke={color} strokeWidth={4} />}
        {type === 'square' && <rect x={5} y={5} width={size - 10} height={size - 10} fill="none" stroke={color} strokeWidth={4} />}
        {type === 'triangle' && <polygon points={`${size/2},5 5,${size-5} ${size-5},${size-5}`} fill="none" stroke={color} strokeWidth={4} />}
      </svg>
    </div>
  );
};

// MAIN SCENE - Implement visual instructions here
const EducationalScene: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  return (
    <AbsoluteFill style={{background: 'linear-gradient(135deg, #0a0a1a 0%, #1a0a2a 100%)'}}>

      {/* EXAMPLE: Render visual instructions with CLEANUP (no overlaps)

      Scene 1: frames 0-150
      {frame >= 0 && frame < 150 && (
        <>
          <Equation text="E = mc²" x={400} y={200} startFrame={0} endFrame={150} size={64} />
        </>
      )}

      Scene 2: frames 150-300 (Scene 1 is GONE)
      {frame >= 150 && frame < 300 && (
        <>
          <Box text="Input" x={100} y={300} width={150} height={80} startFrame={150} />
          <Arrow x1={250} y1={340} x2={400} y2={340} startFrame={180} />
          <Box text="Output" x={400} y={300} width={150} height={80} startFrame={210} />
        </>
      )}

      Scene 3: frames 300-450 (builds on Scene 2 - keep boxes)
      {frame >= 150 && frame < 450 && (
        <>
          <Box text="Input" x={100} y={300} width={150} height={80} startFrame={150} />
          <Box text="Output" x={400} y={300} width={150} height={80} startFrame={210} />
        </>
      )}
      {frame >= 300 && frame < 450 && (
        <GraphAxes startFrame={300} />
      )}

      */}

    </AbsoluteFill>
  );
};

export const RemotionRoot: React.FC = () => (
  <Composition id="EducationalScene" component={EducationalScene} durationInFrames={1800} fps={30} width={1080} height={960} />
);

registerRoot(RemotionRoot);
```

CRITICAL - SCENE CLEANUP (PREVENT OVERLAPS):
- EACH scene must ONLY show content for its time range
- Use conditional rendering: {frame >= startFrame && frame <= endFrame && <Component />}
- Calculate endFrame = nextScene.startFrame OR totalDuration
- OLD content MUST disappear when NEW content starts
- Example WRONG (overlap):
  <Equation text="E=mc²" x={540} y={300} startFrame={0} />
  <Equation text="F=ma" x={540} y={300} startFrame={120} />  // BOTH VISIBLE AT 120!
- Example CORRECT (no overlap):
  {frame >= 0 && frame < 120 && <Equation text="E=mc²" x={540} y={300} startFrame={0} />}
  {frame >= 120 && <Equation text="F=ma" x={540} y={300} startFrame={120} />}

TIMING:
- startFrame = timestamp.start * 30
- endFrame = timestamp.end * 30 (use cleanup array to determine when to hide)
- Fade: interpolate(frame, [start, start+20], [0,1], {extrapolateLeft:'clamp'})
- Spring: spring({frame: frame-start, fps, config: {damping:12}})
- MANDATORY: {frame >= startFrame && frame <= endFrame && <Component />}

LAYOUT (1080x960):
- Center X: 540
- Y zones: top(100-200), center(300-600), bottom(700-850)
- Position: position:'absolute', left:X, top:Y
- NEVER place multiple items at same X,Y coordinates
- If scene builds on previous, keep old elements visible with frame ranges
- If scene is NEW content, hide ALL old elements

STYLING:
- Colors: #00d4ff, #00ff88, #ff00ff
- Background: linear-gradient(135deg, #0a0a1a, #1a0a2a)
- Inline styles only

CRITICAL STRUCTURE (REQUIRED):
1. Import React and Remotion components
2. Define helper components (Equation, Box, etc.)
3. Define EducationalScene component
4. EXPORT RemotionRoot: export const RemotionRoot: React.FC = () => (...)
5. CALL registerRoot: registerRoot(RemotionRoot);

MUST include both:
- export const RemotionRoot: React.FC = () => (...)
- registerRoot(RemotionRoot);

Return ONLY TypeScript code, no explanations."""

        # Format instructions
        instructions_with_timing = []
        for inst in visual_instructions:
            timing_info = {
                "timestamp": inst.get("timestamp", {}),
                "narration": inst.get("narration", ""),
                "visual_type": inst.get("visual_type", ""),
                "description": inst.get("description", ""),
                "elements": inst.get("manim_elements") or inst.get("elements", []),
                "builds_on": inst.get("builds_on", ""),
                "region": inst.get("region", ""),
                "cleanup": inst.get("cleanup", []),
                "transitions": inst.get("transitions", []),
                "properties": inst.get("properties", {}),
                "word_sync": inst.get("word_sync", []),
            }
            instructions_with_timing.append(timing_info)

        instructions_json = json.dumps(instructions_with_timing, indent=2)

        # Check for word_sync data
        has_word_sync = any(inst.get("word_sync") for inst in visual_instructions)
        word_sync_note = ""
        if has_word_sync:
            word_sync_note = "\n\nWORD-SYNC DATA PROVIDED - IMPLEMENT ALL WORD-SYNCHRONIZED ANIMATIONS!"
            word_sync_note += "\nEach scene includes 'word_sync' array with precise timing for dynamic effects."

        # Calculate duration in frames
        duration_frames = int(target_duration * 30)  # 30 fps

        # Format script for context
        script_context = ""
        if script:
            script_context = "\n\nFULL SCRIPT (what's being taught):\n"
            for idx, seg in enumerate(script):
                script_context += f"{idx+1}. {seg.get('speaker', 'Speaker')}: {seg.get('text', '')}\n"

        user_prompt = f"""TEACHING: {topic}
{script_context}
Duration: {duration_frames} frames (30fps)

VISUAL SCENES TO RENDER:
{instructions_json}

YOUR JOB: Render visuals that TEACH the concept based on the script above.

CRITICAL - PREVENT CONTENT OVERLAP:
For EACH scene in the JSON:
1. Calculate startFrame = scene.timestamp.start * 30
2. Calculate endFrame = next_scene.timestamp.start * 30 (OR {duration_frames} if last scene)
3. Wrap ALL components in: {{frame >= startFrame && frame < endFrame && <Component />}}
4. Check "cleanup" field - if it lists elements, those should NOT appear in this scene
5. Check "builds_on" field - if it references previous scene, keep those elements visible

EXAMPLE - TWO SCENES WITH PROPER CLEANUP:
Scene 1: start=0s, end=5s (when scene 2 starts)
Scene 2: start=5s, end=10s

{{/* Scene 1: 0-5 seconds (frames 0-150) */}}
{{frame >= 0 && frame < 150 && (
  <>
    <Equation text="E = mc²" x={{540}} y={{300}} startFrame={{0}} />
  </>
)}}

{{/* Scene 2: 5-10 seconds (frames 150-300) - Scene 1 is GONE */}}
{{frame >= 150 && frame < 300 && (
  <>
    <Equation text="F = ma" x={{540}} y={{300}} startFrame={{150}} />
  </>
)}}

RENDER BY visual_type (with proper cleanup):
- "equation" → {{frame >= start && frame < end && <Equation text="formula" x={{540}} y={{300}} startFrame={{start}} endFrame={{end}} />}}
- "diagram" → {{frame >= start && frame < end && (<><Box .../><Arrow .../><Box .../></>)}}
- "graph" → {{frame >= start && frame < end && (<><GraphAxes .../><PlotCurve .../></>)}}
- "shape" → {{frame >= start && frame < end && <Shape type="circle" ... />}}

Use scene.description to understand WHAT to render (it's specific to this topic!)
Text ONLY for: equations, labels, axes, measurements (NOT narration - subtitles do that)

CRITICAL CHECKLIST FOR EACH SCENE:
✓ Wrapped in {{frame >= X && frame < Y && ...}}
✓ endFrame = next scene's startFrame
✓ No overlapping coordinates if not building on previous
✓ Elements in "cleanup" are NOT rendered

CRITICAL REQUIREMENTS:
- startFrame = timestamp.start * 30
- endFrame = next timestamp.start * 30
- durationInFrames = {duration_frames}
- MUST EXPORT: export const RemotionRoot: React.FC = () => (...)
- MUST END WITH: registerRoot(RemotionRoot);"""

        logger.info("Generating initial Remotion code")

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
        )

        code = response.choices[0].message.content
        messages.append({"role": "assistant", "content": code})

        # Extract code from markdown
        code = self._extract_code_from_markdown(code)

        logger.debug(f"Generated code length: {len(code)} characters")
        return code, messages

    async def _fix_code(
        self,
        broken_code: str,
        error_message: str,
        conversation_history: List[Dict],
        attempt: int,
    ) -> Tuple[str, List[Dict]]:
        """Fix Remotion code based on error feedback."""
        # Truncate code if too long
        code_preview = broken_code if len(broken_code) < 3000 else broken_code[:3000] + "\n... (truncated)"

        error_prompt = f"""The code you generated has an error. Here's what happened:

ERROR:
{error_message}

FAILED CODE (first 3000 chars):
```tsx
{code_preview}
```

This is attempt {attempt + 1}/3. Please analyze the error carefully and fix the code.

CRITICAL DEBUGGING TIPS:
- If validation error about missing imports: Ensure you import all used components from 'remotion'
- If "Missing export" error: You MUST export RemotionRoot: export const RemotionRoot: React.FC = () => ...
- If "Missing registerRoot()" error: You MUST call registerRoot(RemotionRoot) at the end of the file
- If React error #130 (invalid element type): Component is undefined - check all components are defined before use
- If syntax errors: Check all JSX tags are properly closed
- If type errors: Ensure TypeScript types are correct
- Make sure durationInFrames is set to a NUMBER not a variable name
- Ensure all React hooks (useCurrentFrame, useVideoConfig) are imported from 'remotion'

CONTENT OVERLAP FIX (VERY COMMON ISSUE):
If content is rendering on top of each other, you MUST use frame-based conditional rendering:
- BAD: <Equation startFrame={{0}} /> <Equation startFrame={{150}} />  // Both visible at frame 150!
- GOOD: {{frame >= 0 && frame < 150 && <Equation startFrame={{0}} />}}
         {{frame >= 150 && frame < 300 && <Equation startFrame={{150}} />}}

For EACH scene, wrap content in: {{frame >= sceneStart && frame < sceneEnd && (<>...</>)}}

REQUIRED AT END OF FILE (Remotion 4.x):
```tsx
export const RemotionRoot: React.FC = () => (
  <Composition id="EducationalScene" component={EducationalScene} durationInFrames={XXXX} fps={30} width={1080} height={960} />
);

registerRoot(RemotionRoot);
```

Return ONLY the complete fixed TypeScript/React code, no explanations."""

        logger.info(f"Fixing Remotion code based on error (attempt {attempt + 1})")

        conversation_history.append({"role": "user", "content": error_prompt})

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=conversation_history,
            temperature=0.7,
        )

        fixed_code = response.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": fixed_code})

        fixed_code = self._extract_code_from_markdown(fixed_code)

        logger.debug(f"Fixed code attempt {attempt + 1}, length: {len(fixed_code)} characters")
        return fixed_code, conversation_history

    async def _setup_remotion_project(self, output_dir: Path, root_tsx_code: str):
        """Setup Remotion project structure with generated code."""
        logger.info(f"Setting up Remotion project in {output_dir}")

        # Create directory structure (just src folder for the Root.tsx)
        output_dir.mkdir(parents=True, exist_ok=True)
        src_dir = output_dir / "src"
        src_dir.mkdir(exist_ok=True)

        # Write Root.tsx - this is the only file needed per job
        root_file = src_dir / "Root.tsx"
        await asyncio.to_thread(
            root_file.write_text, root_tsx_code, encoding="utf-8"
        )
        logger.info(f"Written Root.tsx to {root_file}")
        logger.info("Remotion project structure created (using shared backend node_modules)")

    async def _validate_code(self, project_dir: Path) -> Tuple[bool, Optional[str]]:
        """
        Validate Remotion code by checking TypeScript syntax.

        Args:
            project_dir: Path to the Remotion project directory

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check if Root.tsx exists
            root_file = project_dir / "src" / "Root.tsx"
            if not root_file.exists():
                return False, "Root.tsx file not found"

            # Read and do basic validation
            code_content = root_file.read_text(encoding="utf-8")

            # Check for required imports
            if "from 'remotion'" not in code_content and 'from "remotion"' not in code_content:
                return False, "Missing Remotion imports"

            # Check for export (needed for component resolution)
            if "export" not in code_content:
                return False, "Missing export statement (export const RemotionRoot)"

            # Check for registerRoot (REQUIRED for Remotion 4.x)
            if "registerRoot" not in code_content:
                return False, "Missing registerRoot() call - REQUIRED for Remotion 4.x"

            # Check for Composition
            if "Composition" not in code_content:
                return False, "Missing Composition component"

            # Check for AbsoluteFill
            if "AbsoluteFill" not in code_content:
                logger.warning("AbsoluteFill not found - layout may be incorrect")

            logger.info("Code validation passed (basic checks)")
            return True, None

        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False, f"Validation error: {str(e)}"

    def _extract_code_from_markdown(self, text: str) -> str:
        """Extract code from markdown code blocks if present."""
        # Try TypeScript/TSX code blocks first
        pattern = r"```(?:tsx|typescript|ts)?\s*\n(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)

        if matches:
            return matches[0].strip()

        # No code blocks found, return original
        return text.strip()

    async def render_remotion_video(
        self,
        project_dir: Path,
        output_path: Path,
        composition_id: str = "EducationalScene",
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> Path:
        """
        Render Remotion code to video using shared backend node_modules.

        Args:
            project_dir: Path to the job's Remotion project directory (contains src/Root.tsx)
            output_path: Path to save rendered video
            composition_id: ID of the composition to render
            progress_callback: Optional callback for progress updates

        Returns:
            Path to the rendered video file

        Raises:
            Exception: If rendering fails
        """
        try:
            if progress_callback:
                progress_callback("Rendering Remotion animation...", 70)

            logger.info(f"Rendering Remotion composition: {composition_id}")

            # Get the backend directory (where shared node_modules is)
            backend_dir = Path(__file__).parent.parent

            # Get absolute paths
            root_tsx_path = (project_dir / "src" / "Root.tsx").absolute()
            output_path_abs = output_path.absolute()

            # Verify Root.tsx exists
            if not root_tsx_path.exists():
                raise Exception(f"Root.tsx not found at {root_tsx_path}")

            # Verify backend has node_modules with @remotion/cli
            backend_node_modules = backend_dir / "node_modules"
            remotion_cli = backend_node_modules / "@remotion" / "cli"

            if not remotion_cli.exists():
                error_msg = (
                    f"@remotion/cli not found in backend node_modules at {remotion_cli}\n"
                    "Run 'npm install' in the backend directory first!"
                )
                logger.error(error_msg)
                raise Exception(error_msg)

            logger.info(f"Using backend node_modules at {backend_node_modules}")
            logger.info(f"Rendering from {root_tsx_path} to {output_path_abs}")

            # Render with Remotion CLI from backend directory
            cmd = [
                "npx",
                "remotion",
                "render",
                str(root_tsx_path),
                composition_id,
                str(output_path_abs),
                "--codec=h264",
            ]

            logger.info(f"Running command: {' '.join(cmd)}")

            result = await asyncio.to_thread(
                subprocess.run,
                cmd,
                cwd=str(backend_dir),  # Run from backend dir where node_modules is
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
            )

            if result.stdout:
                logger.info(f"Remotion stdout: {result.stdout[-1000:]}")
            if result.stderr:
                logger.warning(f"Remotion stderr: {result.stderr[-1000:]}")

            if result.returncode != 0:
                error_msg = f"Remotion rendering failed: {result.stderr}"
                logger.error(error_msg)
                raise Exception(error_msg)

            if not output_path.exists():
                raise Exception(f"Rendered video not found at {output_path}")

            logger.info(f"Video rendered successfully: {output_path}")

            if progress_callback:
                progress_callback("Remotion rendering complete", 85)

            return output_path

        except subprocess.TimeoutExpired:
            error_msg = "Remotion rendering timeout (10 minutes)"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            logger.error(f"Remotion rendering failed: {e}")
            raise Exception(f"Failed to render Remotion video: {e}")

# EduVideo AI - Frontend

A modern, beautiful React frontend for an educational video generation app. Built with Vite, React, TypeScript, and vanilla CSS.

## Features

- Clean, minimal, modern design with gradient color scheme
- Real-time progress updates via WebSocket
- Smooth animations and transitions
- Fully responsive design
- TypeScript for type safety
- Vanilla CSS (no frameworks) with modern techniques
- Error handling and loading states
- Video player with download functionality

## Tech Stack

- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Vanilla CSS** - Custom styling with CSS Grid, Flexbox, and animations
- **WebSocket** - Real-time communication

## Prerequisites

- Node.js (v18 or higher)
- npm or yarn

## Installation

1. Install dependencies:

```bash
npm install
```

## Development

Start the development server:

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## Build

Build for production:

```bash
npm run build
```

Preview production build:

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── App.tsx           # Main application component
│   ├── App.css           # Application styles
│   ├── types.ts          # TypeScript type definitions
│   ├── main.tsx          # Application entry point
│   └── index.css         # Global styles
├── index.html            # HTML template
├── vite.config.ts        # Vite configuration
├── tsconfig.json         # TypeScript configuration
└── package.json          # Dependencies and scripts
```

## API Integration

### Backend Connection

The frontend connects to the backend API at `http://localhost:8000`. Update the API URLs in `App.tsx` if your backend runs on a different port:

```typescript
// HTTP endpoint for starting video generation
const response = await fetch('http://localhost:8000/api/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ topic }),
});

// WebSocket endpoint for progress updates
const wsUrl = `ws://localhost:8000/ws/${jobId}`;
```

### API Types

The frontend expects the following API structure:

**POST /api/generate**
```json
{
  "topic": "string"
}
```

Response:
```json
{
  "jobId": "string",
  "message": "string",
  "websocketUrl": "string (optional)"
}
```

**WebSocket Messages**

Progress update:
```json
{
  "type": "progress",
  "data": {
    "step": "generating_script" | "creating_audio" | "extracting_timestamps" | "planning_visuals" | "generating_animations" | "stitching_video",
    "status": "pending" | "in_progress" | "completed" | "error",
    "message": "string (optional)",
    "progress": number // 0-100 (optional)
  }
}
```

Completion:
```json
{
  "type": "complete",
  "data": {
    "videoUrl": "string",
    "duration": number,
    "topic": "string"
  }
}
```

Error:
```json
{
  "type": "error",
  "message": "string",
  "details": "string (optional)"
}
```

## Pipeline Steps

The app visualizes the following video generation pipeline:

1. **Generating Script** - AI creates the educational script
2. **Creating Audio** - Converts script to natural speech
3. **Extracting Timestamps** - Analyzes audio for timing
4. **Planning Visuals** - Designs animation sequences
5. **Generating Animations** - Creates visual content
6. **Stitching Video** - Combines audio and visuals

## Design System

### Color Scheme

The app uses a purple-gradient theme with the following color palette:

- **Primary**: `#667eea` → `#764ba2` (gradient)
- **Accent**: `#f093fb` → `#f5576c` (gradient)
- **Success**: `#4facfe` → `#00f2fe` (gradient)
- **Background**: Dark gradient (`#0f0c29` → `#302b63` → `#24243e`)

### CSS Custom Properties

All design tokens are defined as CSS custom properties in `App.css` for easy theming:

```css
:root {
  --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --color-text-primary: #ffffff;
  --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.3);
  --radius-xl: 24px;
  --transition-base: 250ms cubic-bezier(0.4, 0, 0.2, 1);
}
```

## Browser Support

- Chrome/Edge (last 2 versions)
- Firefox (last 2 versions)
- Safari (last 2 versions)

## Performance

- Code splitting with Vite
- Lazy loading of components
- Optimized animations with CSS
- WebSocket connection cleanup
- Responsive images and video

## Accessibility

- Semantic HTML
- ARIA labels for interactive elements
- Keyboard navigation support
- Reduced motion support for accessibility
- Focus indicators
- High contrast ratios

## Customization

### Changing Colors

Edit the CSS custom properties in `src/App.css`:

```css
:root {
  --gradient-primary: linear-gradient(135deg, #your-color 0%, #your-color 100%);
  /* ... other properties */
}
```

### Changing Pipeline Steps

Edit the `PIPELINE_STEPS` array in `src/App.tsx`:

```typescript
const PIPELINE_STEPS: StepInfo[] = [
  {
    key: 'your_step',
    label: 'Your Step',
    description: 'Description of your step',
  },
  // ... more steps
];
```

Don't forget to update the `PipelineStep` type in `src/types.ts`.

## Troubleshooting

### WebSocket Connection Issues

If you're experiencing WebSocket connection issues:

1. Ensure the backend is running and accessible
2. Check CORS settings on the backend
3. Verify WebSocket URL is correct
4. Check browser console for errors

### Build Errors

If you encounter build errors:

1. Clear the `node_modules` folder and reinstall:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

2. Clear Vite cache:
   ```bash
   rm -rf .vite
   ```

## Contributing

1. Follow the existing code style
2. Use TypeScript for type safety
3. Write vanilla CSS (no frameworks)
4. Test responsive design
5. Ensure accessibility standards

## License

MIT

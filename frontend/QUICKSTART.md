# Quick Start Guide - EduVideo AI Frontend

## Get Up and Running in 2 Minutes

### Prerequisites
- Node.js 18+ installed
- Backend server ready (or mock server for testing)

### Installation & Run

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (if not already installed)
npm install

# Start development server
npm run dev
```

The app will be available at: **http://localhost:5173**

### First Time Setup

1. **Configure Backend URL** (if different from default):
   - Copy `.env.example` to `.env`
   - Edit the URLs if your backend isn't at `localhost:8000`

2. **Start Backend Server** (required for full functionality):
   - The frontend expects a backend at `http://localhost:8000`
   - See backend documentation for setup

### Testing Without Backend

To test the UI without a backend, you can modify `App.tsx` temporarily:

```typescript
// Comment out the actual fetch and add mock data
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  setIsGenerating(true);

  // Mock progress updates
  setTimeout(() => {
    setProgressSteps(new Map([
      ['generating_script', { step: 'generating_script', status: 'in_progress' }]
    ]));
  }, 1000);
};
```

### Building for Production

```bash
# Build optimized production bundle
npm run build

# Preview production build locally
npm run preview
```

Production files will be in the `dist/` directory.

### Project Structure at a Glance

```
frontend/
├── src/
│   ├── App.tsx          # Main component - START HERE
│   ├── App.css          # All styles
│   ├── types.ts         # TypeScript types - API contract
│   └── main.tsx         # Entry point
├── index.html           # HTML shell
└── package.json         # Dependencies
```

### Key URLs

- **Dev Server**: http://localhost:5173
- **Backend API**: http://localhost:8000/api/generate
- **WebSocket**: ws://localhost:8000/ws/{jobId}

### Common Commands

```bash
npm run dev      # Start dev server with hot reload
npm run build    # Build for production
npm run preview  # Preview production build
npm run lint     # Run ESLint
```

### Troubleshooting

**Port already in use?**
```bash
# Vite will automatically try the next available port
# Or specify a port:
npm run dev -- --port 3000
```

**Build errors?**
```bash
# Clear cache and reinstall
rm -rf node_modules dist .vite
npm install
npm run build
```

**Backend connection issues?**
- Check that backend is running
- Verify URL in browser console
- Check CORS settings on backend
- Look for errors in browser DevTools (F12)

### Next Steps

1. Read `README.md` for full documentation
2. Check `DESIGN_GUIDE.md` for design system
3. Review `types.ts` for API contract
4. Customize colors in `App.css` (CSS variables at top)

### Quick Customization

**Change primary color:**
```css
/* In App.css */
:root {
  --gradient-primary: linear-gradient(135deg, #your-color 0%, #your-color 100%);
}
```

**Change app title:**
```tsx
/* In App.tsx */
<h1 className="title">Your App Name</h1>
```

**Change backend URL:**
```tsx
/* In App.tsx, line ~79 */
const response = await fetch('http://your-backend:port/api/generate', {
```

### Support

For issues or questions:
1. Check browser console (F12) for errors
2. Review `README.md` troubleshooting section
3. Verify backend is running and accessible
4. Check network tab in DevTools

### Features Overview

The app includes:
- Topic input with validation
- Real-time progress via WebSocket
- 6-step pipeline visualization
- Video player on completion
- Error handling
- Responsive design
- Smooth animations
- Dark theme with gradients

Enjoy building with EduVideo AI!

export const theme = {
  colors: {
    background: {
      primary: '#0a0a0a',
      secondary: '#151515',
      tertiary: '#1f1f1f',
      glass: 'rgba(20, 20, 20, 0.85)',
    },
    accent: {
      primary: '#7c3aed',
      secondary: '#6366f1',
      hover: '#8b5cf6',
      glow: 'rgba(124, 58, 237, 0.5)',
    },
    text: {
      primary: '#ffffff',
      secondary: '#a3a3a3',
      muted: '#737373',
    },
    border: {
      primary: 'rgba(255, 255, 255, 0.1)',
      secondary: 'rgba(255, 255, 255, 0.05)',
      accent: 'rgba(124, 58, 237, 0.3)',
    },
    status: {
      recording: '#ef4444',
      success: '#22c55e',
      warning: '#f59e0b',
    },
  },
  shadows: {
    sm: '0 2px 8px rgba(0, 0, 0, 0.3)',
    md: '0 4px 16px rgba(0, 0, 0, 0.4)',
    lg: '0 8px 32px rgba(0, 0, 0, 0.5)',
    glow: '0 0 20px rgba(124, 58, 237, 0.4)',
    glowLg: '0 0 40px rgba(124, 58, 237, 0.6)',
  },
  borderRadius: {
    sm: '6px',
    md: '12px',
    lg: '16px',
    xl: '24px',
    full: '9999px',
  },
  transitions: {
    fast: '150ms cubic-bezier(0.4, 0, 0.2, 1)',
    normal: '250ms cubic-bezier(0.4, 0, 0.2, 1)',
    slow: '350ms cubic-bezier(0.4, 0, 0.2, 1)',
  },
  zIndex: {
    base: 1,
    overlay: 10,
    modal: 100,
    tooltip: 1000,
  },
};

export type Theme = typeof theme;

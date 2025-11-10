# Design Guide - EduVideo AI Frontend

## Color System

### Gradients

```css
/* Primary - Used for main buttons and highlights */
--gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Accent - Used for error states and alerts */
--gradient-accent: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);

/* Success - Used for completion and success states */
--gradient-success: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);

/* Background - Used for main app background */
--gradient-background: linear-gradient(180deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
```

### Solid Colors

```css
/* Primary Colors */
--color-primary: #667eea;        /* Main brand color */
--color-primary-dark: #5568d3;   /* Darker variant */
--color-accent: #f5576c;         /* Accent highlights */
--color-success: #00f2fe;        /* Success state */
--color-error: #ff6b6b;          /* Error state */
--color-warning: #ffd93d;        /* Warning state */

/* Text Colors */
--color-text-primary: #ffffff;              /* Main text (100% opacity) */
--color-text-secondary: rgba(255, 255, 255, 0.8);  /* Secondary text (80%) */
--color-text-tertiary: rgba(255, 255, 255, 0.6);   /* Tertiary text (60%) */

/* Background Colors */
--color-bg-card: rgba(255, 255, 255, 0.08);    /* Card backgrounds */
--color-bg-input: rgba(255, 255, 255, 0.05);   /* Input backgrounds */
--color-border: rgba(255, 255, 255, 0.1);      /* Border color */
```

## Spacing System

```css
/* Based on 8px grid */
xs:  4px   (0.25rem)
sm:  8px   (0.5rem)
md:  16px  (1rem)
lg:  24px  (1.5rem)
xl:  32px  (2rem)
2xl: 48px  (3rem)
3xl: 64px  (4rem)
```

## Typography

### Font Family

```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
  'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
  sans-serif;
```

### Font Sizes

```css
/* Mobile */
.title: 2rem (32px)
.tagline: 0.875rem (14px)
.topic-input: 1rem (16px)
.generate-button: 1.125rem (18px)

/* Desktop */
.title: 3.5rem (56px)
.tagline: 1.25rem (20px)
.topic-input: 1.125rem (18px)
.generate-button: 1.125rem (18px)
```

### Font Weights

- Regular: 400
- Medium: 500
- Semibold: 600
- Bold: 700
- Extrabold: 800

## Shadows

```css
--shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.1);
--shadow-md: 0 4px 16px rgba(0, 0, 0, 0.2);
--shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.3);
--shadow-xl: 0 16px 64px rgba(0, 0, 0, 0.4);
```

## Border Radius

```css
--radius-sm: 8px;
--radius-md: 12px;
--radius-lg: 16px;
--radius-xl: 24px;
```

## Transitions

```css
--transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-base: 250ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-slow: 350ms cubic-bezier(0.4, 0, 0.2, 1);
```

## Animations

### Fade In
```css
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
/* Usage: animation: fadeIn 0.5s ease-out; */
```

### Slide Down
```css
@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
/* Usage: animation: slideDown 0.6s ease-out; */
```

### Slide Up
```css
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
/* Usage: animation: slideUp 0.4s ease-out; */
```

### Spin
```css
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
/* Usage: animation: spin 0.8s linear infinite; */
```

### Glow
```css
@keyframes glow {
  0%, 100% { box-shadow: 0 0 10px rgba(102, 126, 234, 0.2); }
  50% { box-shadow: 0 0 20px rgba(102, 126, 234, 0.4); }
}
/* Usage: animation: glow 2s ease-in-out infinite; */
```

### Pulse
```css
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}
/* Usage: animation: pulse 2s ease-in-out infinite; */
```

### Shake
```css
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-4px); }
  20%, 40%, 60%, 80% { transform: translateX(4px); }
}
/* Usage: animation: shake 0.5s ease-out; */
```

### Scale In
```css
@keyframes scaleIn {
  from {
    transform: scale(0);
  }
  to {
    transform: scale(1);
  }
}
/* Usage: animation: scaleIn 0.3s ease-out; */
```

## Component States

### Button States

```css
/* Default */
background: var(--gradient-primary);
box-shadow: var(--shadow-md);

/* Hover */
transform: translateY(-2px);
box-shadow: var(--shadow-lg);

/* Active/Pressed */
transform: translateY(0);

/* Disabled */
opacity: 0.8;
cursor: not-allowed;

/* Generating */
background: linear-gradient(135deg, #5568d3 0%, #614090 100%);
```

### Input States

```css
/* Default */
border: 2px solid var(--color-border);
background: var(--color-bg-input);

/* Focus */
border-color: var(--color-primary);
box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);

/* Disabled */
opacity: 0.6;
cursor: not-allowed;
```

### Step States

```css
/* Pending */
opacity: 0.5;
background: rgba(255, 255, 255, 0.03);

/* In Progress */
background: rgba(102, 126, 234, 0.1);
border-color: rgba(102, 126, 234, 0.3);
animation: glow 2s ease-in-out infinite;

/* Completed */
background: rgba(0, 242, 254, 0.05);
border-color: rgba(0, 242, 254, 0.2);

/* Error */
background: rgba(255, 107, 107, 0.1);
border-color: rgba(255, 107, 107, 0.3);
```

## Layout Guidelines

### Container
- Max width: 900px
- Centered horizontally
- Padding: 2rem (desktop), 1rem (mobile)

### Cards
- Background: `rgba(255, 255, 255, 0.08)` with backdrop blur
- Border: `1px solid rgba(255, 255, 255, 0.1)`
- Border radius: 24px (xl)
- Padding: 2rem (desktop), 1.5rem (tablet), 1rem (mobile)
- Box shadow: var(--shadow-lg)

### Spacing Between Sections
- Gap: 2rem (32px)

## Glassmorphism Effect

```css
.card {
  background: var(--color-bg-card);
  backdrop-filter: blur(20px);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
}
```

## Responsive Breakpoints

```css
/* Mobile First Approach */

/* Base styles: 0-479px (Mobile) */

/* Small tablets: 480px+ */
@media (max-width: 480px) {
  /* Adjust for very small screens */
}

/* Tablets: 768px+ */
@media (max-width: 768px) {
  /* Adjust for tablets */
}

/* Desktop: 769px+ */
/* Default styles apply */
```

## Icon Usage

### SVG Icons
- Size: 20-24px for inline icons
- Color: currentColor (inherits text color)
- Accessible with proper viewBox

```html
<svg className="icon" viewBox="0 0 20 20" fill="currentColor">
  <path fillRule="evenodd" d="..." clipRule="evenodd" />
</svg>
```

## Accessibility

### Focus States
- Visible outline on all interactive elements
- High contrast focus indicators
- Keyboard navigation support

### Color Contrast
- Text on background: Minimum 4.5:1 ratio
- Large text: Minimum 3:1 ratio
- All important text uses high contrast white

### Reduced Motion
```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Usage Examples

### Creating a New Card

```css
.my-card {
  background: var(--color-bg-card);
  backdrop-filter: blur(20px);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: 2rem;
  box-shadow: var(--shadow-lg);
  transition: transform var(--transition-base), box-shadow var(--transition-base);
}

.my-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-xl);
}
```

### Creating a Gradient Button

```css
.my-button {
  background: var(--gradient-primary);
  border: none;
  border-radius: var(--radius-md);
  padding: 1rem 2rem;
  color: var(--color-text-primary);
  font-weight: 600;
  cursor: pointer;
  transition: transform var(--transition-base);
}

.my-button:hover {
  transform: translateY(-2px);
}
```

### Creating an Animated Element

```css
.my-element {
  animation: fadeIn 0.5s ease-out;
}
```

## Best Practices

1. **Use CSS Custom Properties**: Always use variables for colors, spacing, shadows
2. **Mobile First**: Start with mobile styles, add desktop with media queries
3. **Smooth Transitions**: Use easing functions for natural motion
4. **Consistent Spacing**: Follow the 8px grid system
5. **Accessibility First**: Ensure proper contrast and keyboard navigation
6. **Performance**: Use CSS animations over JavaScript
7. **Semantic HTML**: Use proper HTML elements for better accessibility
8. **Dark Theme**: Design assumes dark background, light text
9. **Glass Effect**: Use backdrop-filter for modern glassmorphism
10. **Hover States**: Add subtle hover effects to interactive elements

## Color Palette Reference

| Color Name | Hex Code | Usage |
|------------|----------|-------|
| Primary Purple | `#667eea` | Primary brand color, buttons |
| Dark Purple | `#764ba2` | Gradient end, accents |
| Pink | `#f093fb` | Accent gradient start |
| Red | `#f5576c` | Error states, alerts |
| Cyan | `#4facfe` | Success gradient start |
| Bright Cyan | `#00f2fe` | Success states, completion |
| Yellow | `#ffd93d` | Warning states |
| Error Red | `#ff6b6b` | Error indicators |
| Dark Blue | `#0f0c29` | Background start |
| Medium Purple | `#302b63` | Background middle |
| Dark Purple | `#24243e` | Background end |
| White | `#ffffff` | Primary text |

## Gradient Combinations

```css
/* Purple Gradient */
linear-gradient(135deg, #667eea 0%, #764ba2 100%)

/* Pink-Red Gradient */
linear-gradient(135deg, #f093fb 0%, #f5576c 100%)

/* Blue-Cyan Gradient */
linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)

/* Background Gradient */
linear-gradient(180deg, #0f0c29 0%, #302b63 50%, #24243e 100%)

/* White Text Gradient */
linear-gradient(135deg, #ffffff 0%, #a8b4ff 100%)
```

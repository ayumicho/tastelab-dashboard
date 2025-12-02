# CSS Directory

This directory contains all stylesheets for the TasteLab Dashboard. The styling approach combines custom CSS with Bootstrap 5 framework to create a modern, responsive, and accessible user interface.

## Overview

The CSS architecture follows a modular approach, separating concerns into distinct files for maintainability and scalability.

## File Structure

```
css/
├── style.css              # Main stylesheet (imports and base styles)
├── base.css               # Typography, colors, global styles
├── components/            # Reusable UI components
│   ├── buttons.css        # Button styles
│   ├── cards.css          # Card components
│   ├── forms.css          # Form elements
│   ├── navbar.css         # Navigation bar
│   └── modals.css         # Modal dialogs
├── pages/                 # Page-specific styles
│   ├── home.css           # Dashboard home
│   ├── experiments.css    # Experiment pages
│   ├── profile.css        # User profile
│   └── auth.css           # Login/signup pages
├── layouts/               # Layout structures
│   ├── grid.css           # Grid systems
│   └── containers.css     # Container layouts
└── utilities/             # Utility classes
    ├── spacing.css        # Margins and padding
    ├── colors.css         # Color utilities
    └── typography.css     # Text utilities
```

## Main Stylesheet

### `style.css`
The primary stylesheet that imports all other CSS files and defines core styles:

```css
/* Import base styles */
@import 'base.css';

/* Import components */
@import 'components/buttons.css';
@import 'components/cards.css';
/* ... */

/* Import page styles */
@import 'pages/home.css';
/* ... */
```

**Include in templates:**
```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
```

## Design System

### Color Palette

```css
:root {
    /* Primary Colors */
    --primary-color: #2563eb;
    --primary-hover: #1d4ed8;
    --primary-light: #dbeafe;
    
    /* Secondary Colors */
    --secondary-color: #64748b;
    --secondary-hover: #475569;
    
    /* Accent Colors */
    --accent-color: #f59e0b;
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --error-color: #ef4444;
    --info-color: #3b82f6;
    
    /* Neutral Colors */
    --white: #ffffff;
    --gray-50: #f9fafb;
    --gray-100: #f3f4f6;
    --gray-200: #e5e7eb;
    --gray-300: #d1d5db;
    --gray-500: #6b7280;
    --gray-700: #374151;
    --gray-900: #111827;
    --black: #000000;
    
    /* Background Colors */
    --bg-primary: #ffffff;
    --bg-secondary: #f9fafb;
    --bg-dark: #1f2937;
}
```

### Typography

```css
:root {
    /* Font Families */
    --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    --font-mono: 'Fira Code', 'Courier New', monospace;
    
    /* Font Sizes */
    --text-xs: 0.75rem;    /* 12px */
    --text-sm: 0.875rem;   /* 14px */
    --text-base: 1rem;     /* 16px */
    --text-lg: 1.125rem;   /* 18px */
    --text-xl: 1.25rem;    /* 20px */
    --text-2xl: 1.5rem;    /* 24px */
    --text-3xl: 1.875rem;  /* 30px */
    --text-4xl: 2.25rem;   /* 36px */
    
    /* Font Weights */
    --font-light: 300;
    --font-normal: 400;
    --font-medium: 500;
    --font-semibold: 600;
    --font-bold: 700;
    
    /* Line Heights */
    --leading-tight: 1.25;
    --leading-normal: 1.5;
    --leading-relaxed: 1.75;
}
```

### Spacing

```css
:root {
    /* Spacing Scale (based on 4px) */
    --space-1: 0.25rem;  /* 4px */
    --space-2: 0.5rem;   /* 8px */
    --space-3: 0.75rem;  /* 12px */
    --space-4: 1rem;     /* 16px */
    --space-5: 1.25rem;  /* 20px */
    --space-6: 1.5rem;   /* 24px */
    --space-8: 2rem;     /* 32px */
    --space-10: 2.5rem;  /* 40px */
    --space-12: 3rem;    /* 48px */
    --space-16: 4rem;    /* 64px */
}
```

### Border Radius

```css
:root {
    --radius-sm: 0.25rem;  /* 4px */
    --radius-md: 0.5rem;   /* 8px */
    --radius-lg: 0.75rem;  /* 12px */
    --radius-xl: 1rem;     /* 16px */
    --radius-full: 9999px; /* Pill shape */
}
```

### Shadows

```css
:root {
    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
    --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.15);
}
```

## Component Styles

### Buttons

```css
.btn {
    padding: var(--space-2) var(--space-4);
    border-radius: var(--radius-md);
    font-weight: var(--font-medium);
    transition: all 0.2s ease;
}

.btn-primary {
    background-color: var(--primary-color);
    color: var(--white);
}

.btn-primary:hover {
    background-color: var(--primary-hover);
}
```

### Cards

```css
.card {
    background: var(--bg-primary);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
    padding: var(--space-6);
}
```

### Forms

```css
.form-control {
    width: 100%;
    padding: var(--space-3) var(--space-4);
    border: 1px solid var(--gray-300);
    border-radius: var(--radius-md);
    font-size: var(--text-base);
}

.form-control:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px var(--primary-light);
}
```

## Responsive Design

### Breakpoints

```css
/* Mobile First Approach */
/* Extra Small: < 576px (default) */
/* Small: ≥ 576px */
@media (min-width: 576px) { }

/* Medium: ≥ 768px */
@media (min-width: 768px) { }

/* Large: ≥ 992px */
@media (min-width: 992px) { }

/* Extra Large: ≥ 1200px */
@media (min-width: 1200px) { }

/* XXL: ≥ 1400px */
@media (min-width: 1400px) { }
```

### Responsive Utilities

```css
/* Hide on mobile */
.d-none-sm {
    display: none;
}

@media (min-width: 768px) {
    .d-none-sm {
        display: block;
    }
}

/* Mobile-only display */
.d-mobile-only {
    display: block;
}

@media (min-width: 768px) {
    .d-mobile-only {
        display: none;
    }
}
```

## Utility Classes

### Spacing Utilities

```css
/* Margin */
.m-0 { margin: 0; }
.m-1 { margin: var(--space-1); }
.m-2 { margin: var(--space-2); }
/* ... */

/* Padding */
.p-0 { padding: 0; }
.p-1 { padding: var(--space-1); }
.p-2 { padding: var(--space-2); }
/* ... */
```

### Text Utilities

```css
.text-center { text-align: center; }
.text-left { text-align: left; }
.text-right { text-align: right; }

.text-primary { color: var(--primary-color); }
.text-secondary { color: var(--secondary-color); }
.text-success { color: var(--success-color); }
.text-danger { color: var(--error-color); }
```

### Display Utilities

```css
.d-none { display: none; }
.d-block { display: block; }
.d-inline-block { display: inline-block; }
.d-flex { display: flex; }
.d-grid { display: grid; }
```

## Page-Specific Styles

### Dashboard Home

```css
/* home.css */
.dashboard-header {
    background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
    color: var(--white);
    padding: var(--space-8);
    border-radius: var(--radius-lg);
}

.stats-card {
    text-align: center;
    padding: var(--space-6);
}

.stats-number {
    font-size: var(--text-4xl);
    font-weight: var(--font-bold);
    color: var(--primary-color);
}
```

### Experiment Pages

```css
/* experiments.css */
.experiment-card {
    border-left: 4px solid var(--primary-color);
    transition: transform 0.2s ease;
}

.experiment-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}

.experiment-status {
    display: inline-block;
    padding: var(--space-1) var(--space-3);
    border-radius: var(--radius-full);
    font-size: var(--text-sm);
    font-weight: var(--font-medium);
}
```

## Best Practices

### CSS Organization

1. **Use CSS variables** for consistent theming
2. **Follow BEM naming convention** for component classes
3. **Keep specificity low** - avoid deep nesting
4. **Mobile-first responsive design** - use min-width media queries
5. **Group related styles** together

### Performance

1. **Minimize CSS files** for production
2. **Remove unused styles** regularly
3. **Use shorthand properties** when possible
4. **Avoid @import in production** - concatenate files instead
5. **Optimize selector performance** - avoid universal selectors

### Maintainability

1. **Comment complex styles** with explanations
2. **Use consistent formatting** - 2-space indentation
3. **Organize properties** logically (positioning, box model, typography, visual)
4. **Keep files focused** - one component per file
5. **Document custom properties** in comments

## Dark Mode Support

```css
/* Dark mode variables */
@media (prefers-color-scheme: dark) {
    :root {
        --bg-primary: #1f2937;
        --bg-secondary: #111827;
        --text-primary: #f9fafb;
        --text-secondary: #d1d5db;
    }
}

/* Manual dark mode toggle */
[data-theme="dark"] {
    --bg-primary: #1f2937;
    --bg-secondary: #111827;
    --text-primary: #f9fafb;
}
```

## Browser Compatibility

Styles are compatible with:
- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Adding New Styles

When adding new CSS:

1. **Determine the appropriate file** (component, page, or utility)
2. **Use existing variables** from design system
3. **Follow naming conventions** (BEM for components)
4. **Test responsiveness** across breakpoints
5. **Check browser compatibility**
6. **Document complex styles** with comments
7. **Update this README** if adding new files

## Common Patterns

### Centered Content

```css
.center-content {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
}
```

### Flexible Grid

```css
.grid-auto {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: var(--space-6);
}
```

### Card Hover Effect

```css
.card-hover {
    transition: all 0.3s ease;
}

.card-hover:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-xl);
}
```

## Troubleshooting

### Styles not applying
- Check CSS file is linked in template
- Verify correct class name spelling
- Check for specificity conflicts
- Clear browser cache
- Inspect element in browser dev tools

### Layout issues
- Check for conflicting Bootstrap classes
- Verify parent container has proper display property
- Use browser dev tools to inspect box model
- Check for overflow issues

---

**Last Updated:** December 2025
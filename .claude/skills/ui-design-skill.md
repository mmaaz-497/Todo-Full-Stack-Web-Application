# UI Design System - Todo App

**Version**: 1.0.0
**Stack**: Next.js 16, React 19, Tailwind CSS v4, TypeScript
**Last Updated**: 2025-12-21

---

## Design Philosophy

### Core Principles

- **Modern Minimalism**: Clean interfaces with purposeful whitespace. Every element serves a function.
- **Professional Approachability**: Sophisticated enough for professionals, friendly enough for casual users.
- **Subtle Depth**: Use layering, shadows, and blur effects to create visual hierarchy without overwhelming.
- **Delightful Interactions**: Micro-animations that provide feedback and enhance usability, never just decoration.
- **Accessibility First**: AAA contrast ratios, keyboard navigation, reduced motion support, semantic HTML.
- **Performance**: Animations use GPU-accelerated properties (transform, opacity). Avoid layout thrashing.

### Design Values

1. **Clarity over Cleverness**: Users should instantly understand what to do
2. **Consistency over Novelty**: Repeated patterns reduce cognitive load
3. **Feedback over Silence**: Every action deserves a reaction
4. **Progressive Enhancement**: Core functionality works without JavaScript

---

## Color System

### Primary Palette

#### Primary Color (Brand & Actions)
```css
--primary-50:  #f0f9ff;   /* Lightest tint */
--primary-100: #e0f2fe;
--primary-200: #bae6fd;
--primary-300: #7dd3fc;
--primary-400: #38bdf8;
--primary-500: #0ea5e9;   /* Main brand color */
--primary-600: #0284c7;   /* Hover state */
--primary-700: #0369a1;   /* Active state */
--primary-800: #075985;
--primary-900: #0c4a6e;   /* Darkest shade */
```

#### Secondary/Accent Color (Highlights & Badges)
```css
--accent-50:  #fdf4ff;
--accent-100: #fae8ff;
--accent-200: #f5d0fe;
--accent-300: #f0abfc;
--accent-400: #e879f9;
--accent-500: #d946ef;    /* Main accent */
--accent-600: #c026d3;    /* Hover */
--accent-700: #a21caf;
--accent-800: #86198f;
--accent-900: #701a75;
```

### Neutral Scale (Grays)
```css
--neutral-50:  #fafafa;   /* Near-white backgrounds */
--neutral-100: #f5f5f5;   /* Card backgrounds */
--neutral-200: #e5e5e5;   /* Borders, dividers */
--neutral-300: #d4d4d4;   /* Disabled borders */
--neutral-400: #a3a3a3;   /* Placeholder text */
--neutral-500: #737373;   /* Secondary text */
--neutral-600: #525252;   /* Body text */
--neutral-700: #404040;   /* Headings */
--neutral-800: #262626;   /* Strong emphasis */
--neutral-900: #171717;   /* Near-black */
--neutral-950: #0a0a0a;   /* Pure black alternative */
```

### Semantic Colors

#### Success (Green)
```css
--success-50:  #f0fdf4;
--success-100: #dcfce7;
--success-500: #22c55e;   /* Checkmarks, confirmations */
--success-600: #16a34a;   /* Hover */
--success-700: #15803d;   /* Active */
```

#### Warning (Amber)
```css
--warning-50:  #fffbeb;
--warning-100: #fef3c7;
--warning-500: #f59e0b;   /* Warnings, alerts */
--warning-600: #d97706;
--warning-700: #b45309;
```

#### Error (Red)
```css
--error-50:  #fef2f2;
--error-100: #fee2e2;
--error-500: #ef4444;     /* Errors, delete actions */
--error-600: #dc2626;     /* Hover */
--error-700: #b91c1c;     /* Active */
```

#### Info (Blue)
```css
--info-50:  #eff6ff;
--info-100: #dbeafe;
--info-500: #3b82f6;      /* Info messages */
--info-600: #2563eb;
--info-700: #1d4ed8;
```

### Background Colors
```css
--bg-main:      #ffffff;       /* Main page background */
--bg-card:      #ffffff;       /* Card/panel background */
--bg-elevated:  #ffffff;       /* Modals, dropdowns (use with shadow) */
--bg-subtle:    var(--neutral-50);  /* Subtle sections */
--bg-muted:     var(--neutral-100); /* Disabled backgrounds */
```

### Dark Mode (Optional)
```css
[data-theme="dark"] {
  --bg-main:      #0a0a0a;
  --bg-card:      #171717;
  --bg-elevated:  #262626;
  --bg-subtle:    #171717;
  --neutral-50:   #262626;
  --neutral-900:  #fafafa;
  /* Invert neutral scale for dark mode */
}
```

### Accessibility Standards

**All text must meet:**
- Normal text (< 18px): 7:1 contrast ratio (AAA)
- Large text (≥ 18px or 14px bold): 4.5:1 contrast ratio (AA)
- Interactive elements: 3:1 contrast ratio for visual boundaries

**Recommended Combinations:**
- Primary-600 text on white: ✓ AAA compliant
- Neutral-600 body text on white: ✓ AAA compliant
- Neutral-500 secondary text on white: ✓ AA compliant
- White text on Primary-600: ✓ AAA compliant

---

## Typography

### Font Families

```css
/* Primary: Google Fonts - Inter (Sans-serif) */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Secondary/Monospace: JetBrains Mono */
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');

--font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
--font-mono: 'JetBrains Mono', 'Courier New', monospace;
```

### Font Size Scale

```css
--text-xs:   0.75rem;    /* 12px - Tiny labels, timestamps */
--text-sm:   0.875rem;   /* 14px - Secondary text, captions */
--text-base: 1rem;       /* 16px - Body text (default) */
--text-lg:   1.125rem;   /* 18px - Emphasized body text */
--text-xl:   1.25rem;    /* 20px - Small headings */
--text-2xl:  1.5rem;     /* 24px - Section headings */
--text-3xl:  1.875rem;   /* 30px - Page headings */
--text-4xl:  2.25rem;    /* 36px - Hero headings */
--text-5xl:  3rem;       /* 48px - Landing page hero */
```

### Line Heights

```css
--leading-none:   1;        /* Tight headings */
--leading-tight:  1.25;     /* Headings */
--leading-snug:   1.375;    /* UI elements */
--leading-normal: 1.5;      /* Body text (default) */
--leading-relaxed: 1.625;   /* Long-form content */
--leading-loose:  2;        /* Spacious layouts */
```

### Letter Spacing

```css
--tracking-tighter: -0.05em;  /* Large headings */
--tracking-tight:   -0.025em; /* Headings */
--tracking-normal:  0;        /* Body text */
--tracking-wide:    0.025em;  /* Button text, labels */
--tracking-wider:   0.05em;   /* ALL CAPS labels */
```

### Font Weights

```css
--font-light:     300;  /* Rarely used, elegant touches */
--font-normal:    400;  /* Body text */
--font-medium:    500;  /* Emphasis, strong body text */
--font-semibold:  600;  /* Buttons, headings */
--font-bold:      700;  /* Strong headings, important CTAs */
```

### Usage Guidelines

| Element | Size | Weight | Line Height | Letter Spacing |
|---------|------|--------|-------------|----------------|
| Hero Title (Landing) | 5xl | bold | tight | tighter |
| Page Title | 3xl | bold | tight | tight |
| Section Heading | 2xl | semibold | tight | normal |
| Card Heading | xl | semibold | snug | normal |
| Body Text | base | normal | normal | normal |
| Secondary Text | sm | normal | normal | normal |
| Button Text | base | semibold | snug | wide |
| Input Label | sm | medium | snug | normal |
| Caption/Timestamp | xs | normal | normal | normal |

---

## Spacing & Layout

### Spacing Scale

**Base Unit**: 4px (0.25rem)

```css
--space-0:   0;
--space-1:   0.25rem;   /* 4px  - Tight spacing */
--space-2:   0.5rem;    /* 8px  - Icon-text gap */
--space-3:   0.75rem;   /* 12px - Small padding */
--space-4:   1rem;      /* 16px - Default padding */
--space-5:   1.25rem;   /* 20px - Medium padding */
--space-6:   1.5rem;    /* 24px - Large padding */
--space-8:   2rem;      /* 32px - Section spacing */
--space-10:  2.5rem;    /* 40px - Large sections */
--space-12:  3rem;      /* 48px - Major sections */
--space-16:  4rem;      /* 64px - Hero sections */
--space-20:  5rem;      /* 80px - Extra large */
--space-24:  6rem;      /* 96px - Spacious layouts */
```

### Container Max-Widths

```css
--container-xs:   20rem;    /* 320px - Tiny modals */
--container-sm:   24rem;    /* 384px - Narrow forms */
--container-md:   28rem;    /* 448px - Auth forms */
--container-lg:   32rem;    /* 512px - Standard forms */
--container-xl:   36rem;    /* 576px - Wide modals */
--container-2xl:  42rem;    /* 672px - Content cards */
--container-3xl:  48rem;    /* 768px - Article width */
--container-4xl:  56rem;    /* 896px - Dashboard content */
--container-5xl:  64rem;    /* 1024px - Wide content */
--container-6xl:  72rem;    /* 1152px - Max content */
--container-7xl:  80rem;    /* 1280px - Full width dashboard */
```

### Responsive Breakpoints

```css
/* Tailwind default breakpoints - DO NOT change these */
--screen-sm:  640px;   /* Mobile landscape */
--screen-md:  768px;   /* Tablet portrait */
--screen-lg:  1024px;  /* Tablet landscape */
--screen-xl:  1280px;  /* Desktop */
--screen-2xl: 1536px;  /* Large desktop */
```

### Grid System

**12-Column Grid** for complex layouts:
```tsx
<div className="grid grid-cols-12 gap-6">
  <div className="col-span-12 md:col-span-8">Main content</div>
  <div className="col-span-12 md:col-span-4">Sidebar</div>
</div>
```

**Auto-fit Grid** for card layouts:
```tsx
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
  {/* Cards */}
</div>
```

---

## Component Specifications

### Buttons

#### Primary Button
```tsx
className="
  px-6 py-2.5
  bg-primary-600 hover:bg-primary-700 active:bg-primary-800
  text-white font-semibold tracking-wide
  rounded-lg
  shadow-md hover:shadow-lg
  transform hover:scale-[1.02] active:scale-[0.98]
  transition-all duration-200 ease-out
  focus:outline-none focus:ring-4 focus:ring-primary-200
  disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none
"
```

**States:**
- Default: bg-primary-600, shadow-md
- Hover: bg-primary-700, scale up 2%, shadow-lg
- Active: bg-primary-800, scale down 2%
- Focus: ring-4 ring-primary-200 (keyboard navigation)
- Disabled: opacity-50, no pointer events

#### Secondary Button
```tsx
className="
  px-6 py-2.5
  bg-transparent hover:bg-neutral-100 active:bg-neutral-200
  text-primary-600 hover:text-primary-700 font-semibold tracking-wide
  border-2 border-primary-600 hover:border-primary-700
  rounded-lg
  transform hover:scale-[1.02] active:scale-[0.98]
  transition-all duration-200 ease-out
  focus:outline-none focus:ring-4 focus:ring-primary-200
  disabled:opacity-50 disabled:cursor-not-allowed
"
```

#### Ghost Button
```tsx
className="
  px-4 py-2
  bg-transparent hover:bg-neutral-100 active:bg-neutral-200
  text-neutral-700 hover:text-neutral-900 font-medium
  rounded-md
  transition-colors duration-150 ease-out
  focus:outline-none focus:ring-2 focus:ring-neutral-300
"
```

#### Danger Button
```tsx
className="
  px-6 py-2.5
  bg-error-600 hover:bg-error-700 active:bg-error-800
  text-white font-semibold tracking-wide
  rounded-lg
  shadow-md hover:shadow-lg
  transform hover:scale-[1.02] active:scale-[0.98]
  transition-all duration-200 ease-out
  focus:outline-none focus:ring-4 focus:ring-error-200
"
```

#### Icon Button
```tsx
className="
  p-2.5
  bg-transparent hover:bg-neutral-100 active:bg-neutral-200
  text-neutral-600 hover:text-neutral-900
  rounded-lg
  transition-all duration-150 ease-out
  focus:outline-none focus:ring-2 focus:ring-neutral-300
"
```

### Input Fields

#### Text Input (Default State)
```tsx
className="
  w-full px-4 py-2.5
  bg-white border-2 border-neutral-300
  text-neutral-900 placeholder:text-neutral-400
  rounded-lg
  transition-all duration-200 ease-out
  focus:outline-none focus:border-primary-500 focus:ring-4 focus:ring-primary-100
  hover:border-neutral-400
"
```

#### Input with Floating Label Pattern
```tsx
<div className="relative">
  <input
    id="email"
    type="email"
    className="
      peer w-full px-4 pt-6 pb-2
      bg-white border-2 border-neutral-300
      rounded-lg
      transition-all duration-200
      focus:outline-none focus:border-primary-500 focus:ring-4 focus:ring-primary-100
      placeholder-transparent
    "
    placeholder="Email"
  />
  <label
    htmlFor="email"
    className="
      absolute left-4 top-2
      text-xs text-neutral-500 font-medium
      transition-all duration-200
      peer-placeholder-shown:text-base peer-placeholder-shown:top-4
      peer-focus:text-xs peer-focus:top-2 peer-focus:text-primary-600
    "
  >
    Email address
  </label>
</div>
```

#### Input Error State
```tsx
className="
  w-full px-4 py-2.5
  bg-error-50 border-2 border-error-500
  text-neutral-900 placeholder:text-error-300
  rounded-lg
  transition-all duration-200
  focus:outline-none focus:border-error-600 focus:ring-4 focus:ring-error-100
"

// Error message below:
<p className="mt-1.5 text-sm text-error-600 flex items-center gap-1">
  <ErrorIcon className="w-4 h-4" />
  <span>This field is required</span>
</p>
```

#### Input Disabled State
```tsx
className="
  w-full px-4 py-2.5
  bg-neutral-100 border-2 border-neutral-300
  text-neutral-500
  rounded-lg
  cursor-not-allowed
"
```

#### Input with Icon
```tsx
<div className="relative">
  <input
    className="w-full pl-11 pr-4 py-2.5 ..."
  />
  <div className="absolute left-4 top-1/2 -translate-y-1/2 text-neutral-400">
    <SearchIcon className="w-5 h-5" />
  </div>
</div>
```

### Cards

#### Standard Card
```tsx
className="
  bg-white
  rounded-xl
  shadow-sm hover:shadow-md
  border border-neutral-200
  overflow-hidden
  transition-all duration-300 ease-out
  hover:-translate-y-1
"
```

#### Card with Hover Lift
```tsx
className="
  group
  bg-white
  rounded-xl
  shadow-md hover:shadow-xl
  border border-neutral-200 hover:border-neutral-300
  overflow-hidden
  transform hover:-translate-y-2
  transition-all duration-300 ease-out
  cursor-pointer
"
```

#### Elevated Card (for modals, popovers)
```tsx
className="
  bg-white
  rounded-2xl
  shadow-2xl
  border border-neutral-200
  backdrop-blur-sm
  overflow-hidden
"
```

### Navigation Bar

#### Sticky Navigation with Blur
```tsx
className="
  sticky top-0 z-50
  bg-white/80 backdrop-blur-md
  border-b border-neutral-200
  shadow-sm
  transition-all duration-300
"
```

#### Navigation Links
```tsx
// Active link:
className="
  px-4 py-2
  text-primary-600 font-semibold
  border-b-2 border-primary-600
  transition-colors duration-200
"

// Inactive link:
className="
  px-4 py-2
  text-neutral-600 hover:text-neutral-900 font-medium
  border-b-2 border-transparent hover:border-neutral-300
  transition-all duration-200
"
```

### Links

#### Inline Link
```tsx
className="
  text-primary-600 hover:text-primary-700
  font-medium
  underline underline-offset-2 decoration-2 decoration-primary-300
  hover:decoration-primary-600
  transition-all duration-200
"
```

#### Animated Underline Link
```tsx
className="
  relative
  text-primary-600 font-medium
  after:absolute after:bottom-0 after:left-0
  after:h-0.5 after:w-0 after:bg-primary-600
  after:transition-all after:duration-300
  hover:after:w-full
"
```

### Checkboxes & Toggles

#### Custom Checkbox
```tsx
<label className="flex items-center gap-3 cursor-pointer group">
  <input
    type="checkbox"
    className="
      peer sr-only
    "
  />
  <div className="
    relative w-5 h-5
    bg-white border-2 border-neutral-400
    rounded
    transition-all duration-200
    peer-checked:bg-primary-600 peer-checked:border-primary-600
    peer-focus:ring-4 peer-focus:ring-primary-100
    group-hover:border-neutral-500
  ">
    <svg
      className="
        absolute inset-0 w-full h-full
        text-white opacity-0
        peer-checked:opacity-100
        transition-opacity duration-200
      "
      viewBox="0 0 20 20"
      fill="currentColor"
    >
      <path d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"/>
    </svg>
  </div>
  <span className="text-neutral-700 group-hover:text-neutral-900 transition-colors">
    Remember me
  </span>
</label>
```

#### Toggle Switch
```tsx
<label className="flex items-center gap-3 cursor-pointer">
  <input type="checkbox" className="sr-only peer" />
  <div className="
    relative w-11 h-6
    bg-neutral-300 peer-checked:bg-primary-600
    rounded-full
    transition-colors duration-300
    peer-focus:ring-4 peer-focus:ring-primary-100
  ">
    <div className="
      absolute top-0.5 left-0.5
      w-5 h-5
      bg-white
      rounded-full
      shadow-md
      transform transition-transform duration-300
      peer-checked:translate-x-5
    " />
  </div>
  <span className="text-neutral-700">Dark mode</span>
</label>
```

### Badges & Tags

#### Badge
```tsx
// Success badge:
className="
  inline-flex items-center gap-1
  px-2.5 py-1
  bg-success-100 text-success-700
  text-xs font-semibold tracking-wide uppercase
  rounded-full
"

// Primary badge:
className="
  inline-flex items-center gap-1
  px-2.5 py-1
  bg-primary-100 text-primary-700
  text-xs font-semibold tracking-wide uppercase
  rounded-full
"
```

#### Removable Tag
```tsx
<span className="
  inline-flex items-center gap-2
  px-3 py-1.5
  bg-neutral-100 hover:bg-neutral-200
  text-neutral-700 text-sm font-medium
  rounded-lg
  transition-colors duration-200
">
  <span>Design</span>
  <button className="
    hover:text-error-600 transition-colors
    focus:outline-none focus:ring-2 focus:ring-neutral-300 rounded
  ">
    <XIcon className="w-4 h-4" />
  </button>
</span>
```

### Modal/Dialog

#### Modal Overlay
```tsx
className="
  fixed inset-0 z-50
  bg-neutral-900/50 backdrop-blur-sm
  flex items-center justify-center
  p-4
  animate-fadeIn
"
```

#### Modal Content
```tsx
className="
  relative
  bg-white
  rounded-2xl
  shadow-2xl
  max-w-md w-full
  max-h-[90vh] overflow-y-auto
  animate-slideUp
"
```

### Toast Notifications

#### Success Toast
```tsx
className="
  flex items-start gap-3
  px-4 py-3
  bg-white
  border-l-4 border-success-500
  rounded-lg
  shadow-lg
  animate-slideInRight
"
```

#### Error Toast
```tsx
className="
  flex items-start gap-3
  px-4 py-3
  bg-white
  border-l-4 border-error-500
  rounded-lg
  shadow-lg
  animate-slideInRight
"
```

---

## Animation Guidelines

### Core Animation Principles

1. **Performance First**: Only animate `transform` and `opacity` (GPU-accelerated)
2. **Purposeful Motion**: Every animation should provide feedback or guide attention
3. **Consistent Timing**: Use the duration scale consistently across the app
4. **Respect Accessibility**: Always respect `prefers-reduced-motion`

### Duration Scale

```css
--duration-instant: 100ms;   /* Instant feedback (hover highlights) */
--duration-fast:    150ms;   /* Quick transitions (color changes) */
--duration-normal:  200ms;   /* Default transitions (button hover) */
--duration-medium:  300ms;   /* Smooth transitions (card lift) */
--duration-slow:    400ms;   /* Deliberate animations (modals) */
--duration-slower:  500ms;   /* Complex animations (page transitions) */
--duration-slowest: 600ms;   /* Hero animations */
```

### Easing Functions

```css
/* Use Tailwind's built-in easings */
--ease-linear:     linear;           /* Continuous motion (loading spinners) */
--ease-in:         cubic-bezier(0.4, 0, 1, 1);        /* Accelerating */
--ease-out:        cubic-bezier(0, 0, 0.2, 1);        /* Decelerating (DEFAULT) */
--ease-in-out:     cubic-bezier(0.4, 0, 0.2, 1);      /* Smooth start and end */
--ease-bounce:     cubic-bezier(0.68, -0.55, 0.265, 1.55);  /* Playful bounce */
--ease-spring:     cubic-bezier(0.175, 0.885, 0.32, 1.275); /* Spring effect */
```

**When to Use:**
- `ease-out`: Most UI transitions (buttons, hovers) - feels responsive
- `ease-in-out`: Modal animations, page transitions
- `ease-in`: Elements leaving the screen
- `ease-bounce`: Celebratory animations (task completion)

### Tailwind CSS Animations

Add to `tailwind.config.ts`:

```typescript
theme: {
  extend: {
    animation: {
      // Fade animations
      'fadeIn': 'fadeIn 400ms ease-out',
      'fadeOut': 'fadeOut 300ms ease-in',

      // Slide animations
      'slideUp': 'slideUp 400ms ease-out',
      'slideDown': 'slideDown 400ms ease-out',
      'slideInRight': 'slideInRight 300ms ease-out',
      'slideInLeft': 'slideInLeft 300ms ease-out',
      'slideOutRight': 'slideOutRight 300ms ease-in',

      // Scale animations
      'scaleIn': 'scaleIn 200ms ease-out',
      'scaleOut': 'scaleOut 200ms ease-in',

      // Special effects
      'shimmer': 'shimmer 2s infinite',
      'pulse-soft': 'pulseSoft 2s ease-in-out infinite',
      'bounce-soft': 'bounceSoft 1s ease-in-out',
      'shake': 'shake 400ms ease-in-out',

      // Loading
      'spin-slow': 'spin 1.5s linear infinite',
      'ping-slow': 'ping 2s cubic-bezier(0, 0, 0.2, 1) infinite',
    },

    keyframes: {
      fadeIn: {
        '0%': { opacity: '0' },
        '100%': { opacity: '1' },
      },
      fadeOut: {
        '0%': { opacity: '1' },
        '100%': { opacity: '0' },
      },
      slideUp: {
        '0%': { transform: 'translateY(20px)', opacity: '0' },
        '100%': { transform: 'translateY(0)', opacity: '1' },
      },
      slideDown: {
        '0%': { transform: 'translateY(-20px)', opacity: '0' },
        '100%': { transform: 'translateY(0)', opacity: '1' },
      },
      slideInRight: {
        '0%': { transform: 'translateX(100%)', opacity: '0' },
        '100%': { transform: 'translateX(0)', opacity: '1' },
      },
      slideInLeft: {
        '0%': { transform: 'translateX(-100%)', opacity: '0' },
        '100%': { transform: 'translateX(0)', opacity: '1' },
      },
      slideOutRight: {
        '0%': { transform: 'translateX(0)', opacity: '1' },
        '100%': { transform: 'translateX(100%)', opacity: '0' },
      },
      scaleIn: {
        '0%': { transform: 'scale(0.9)', opacity: '0' },
        '100%': { transform: 'scale(1)', opacity: '1' },
      },
      scaleOut: {
        '0%': { transform: 'scale(1)', opacity: '1' },
        '100%': { transform: 'scale(0.9)', opacity: '0' },
      },
      shimmer: {
        '0%': { backgroundPosition: '-1000px 0' },
        '100%': { backgroundPosition: '1000px 0' },
      },
      pulseSoft: {
        '0%, 100%': { opacity: '1' },
        '50%': { opacity: '0.7' },
      },
      bounceSoft: {
        '0%, 100%': { transform: 'translateY(0)' },
        '50%': { transform: 'translateY(-10px)' },
      },
      shake: {
        '0%, 100%': { transform: 'translateX(0)' },
        '10%, 30%, 50%, 70%, 90%': { transform: 'translateX(-4px)' },
        '20%, 40%, 60%, 80%': { transform: 'translateX(4px)' },
      },
    },
  },
}
```

### Specific Animation Patterns

#### Page Load Animation
```tsx
<div className="animate-fadeIn">
  {/* Page content */}
</div>
```

#### Button Hover Effect
```tsx
className="
  transform hover:scale-105 hover:shadow-lg
  active:scale-95
  transition-all duration-200 ease-out
"
```

#### Input Focus Animation
```tsx
className="
  border-2 border-neutral-300
  focus:border-primary-500 focus:ring-4 focus:ring-primary-100
  transition-all duration-200 ease-out
"
```

#### Card Hover Lift
```tsx
className="
  shadow-md hover:shadow-xl
  transform hover:-translate-y-2
  transition-all duration-300 ease-out
"
```

#### Checkbox Completion Animation
```tsx
// Checkmark appears with scale + opacity
<svg className="
  scale-0 opacity-0
  peer-checked:scale-100 peer-checked:opacity-100
  transition-all duration-300 ease-bounce
">
  {/* Checkmark path */}
</svg>
```

#### Task Completion Animation
```tsx
// Strikethrough + fade
<div className="
  group
  transition-all duration-300
  data-[completed=true]:opacity-60
">
  <span className="
    relative
    after:absolute after:left-0 after:top-1/2 after:h-0.5
    after:w-0 after:bg-neutral-900
    after:transition-all after:duration-500 after:ease-out
    group-data-[completed=true]:after:w-full
  ">
    Task text
  </span>
</div>
```

#### Delete Animation (Slide Out + Fade)
```tsx
// Trigger with state, then remove from DOM
className="
  transition-all duration-300 ease-in
  data-[removing=true]:translate-x-full data-[removing=true]:opacity-0
"
```

#### Staggered List Animation
```tsx
{items.map((item, index) => (
  <div
    key={item.id}
    className="animate-slideUp"
    style={{
      animationDelay: `${index * 50}ms`,
      animationFillMode: 'backwards'
    }}
  >
    {item.content}
  </div>
))}
```

#### Loading Skeleton
```tsx
className="
  bg-gradient-to-r from-neutral-200 via-neutral-300 to-neutral-200
  bg-[length:1000px_100%]
  animate-shimmer
  rounded-lg
"
```

#### Spinner
```tsx
<div className="
  w-8 h-8
  border-4 border-neutral-200 border-t-primary-600
  rounded-full
  animate-spin
" />
```

#### Ripple Effect (Click Feedback)
```tsx
// Requires JavaScript, but CSS setup:
<button className="relative overflow-hidden">
  <span className="relative z-10">Click me</span>
  <span className="
    absolute inset-0 bg-white/30
    scale-0
    transition-transform duration-500 ease-out
    [&.ripple-active]:scale-150
  " />
</button>
```

#### Success Confirmation Animation
```tsx
<div className="
  flex items-center gap-2
  text-success-600
  animate-slideDown
">
  <svg className="w-6 h-6 animate-scaleIn">
    {/* Checkmark */}
  </svg>
  <span>Task completed!</span>
</div>
```

### Accessibility: Reduced Motion

**Always include this in global CSS:**

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

**Tailwind utility:**
```tsx
className="
  motion-safe:animate-slideUp
  motion-reduce:opacity-100
"
```

---

## Specific Page Guidelines

### Landing Page

#### Hero Section
```tsx
<section className="
  relative overflow-hidden
  min-h-screen
  flex items-center justify-center
  bg-gradient-to-br from-primary-50 via-white to-accent-50
  animate-fadeIn
">
  <div className="container max-w-6xl px-6 py-20 text-center">
    <h1 className="
      text-5xl md:text-6xl font-bold
      text-neutral-900
      leading-tight tracking-tighter
      animate-slideUp
    ">
      Organize Your Life, <br />
      <span className="text-primary-600">One Task at a Time</span>
    </h1>

    <p className="
      mt-6 text-lg md:text-xl
      text-neutral-600
      max-w-2xl mx-auto
      leading-relaxed
      animate-slideUp
      [animation-delay:100ms]
    ">
      A beautifully simple todo app that helps you focus on what matters.
    </p>

    <div className="
      mt-10 flex flex-col sm:flex-row gap-4 justify-center
      animate-slideUp
      [animation-delay:200ms]
    ">
      <button className="
        px-8 py-4
        bg-primary-600 hover:bg-primary-700
        text-white text-lg font-semibold tracking-wide
        rounded-xl
        shadow-lg hover:shadow-2xl
        transform hover:scale-105 active:scale-95
        transition-all duration-300 ease-out
      ">
        Get Started Free
      </button>

      <button className="
        px-8 py-4
        bg-white hover:bg-neutral-50
        text-primary-600 text-lg font-semibold tracking-wide
        border-2 border-neutral-300 hover:border-primary-600
        rounded-xl
        shadow-md hover:shadow-lg
        transform hover:scale-105 active:scale-95
        transition-all duration-300 ease-out
      ">
        Watch Demo
      </button>
    </div>
  </div>

  {/* Animated gradient blob (optional) */}
  <div className="
    absolute -top-40 -right-40
    w-96 h-96
    bg-gradient-to-br from-primary-400/20 to-accent-400/20
    rounded-full blur-3xl
    animate-pulse-soft
  " />
</section>
```

#### Feature Cards
```tsx
<div className="
  grid grid-cols-1 md:grid-cols-3 gap-8
  container max-w-6xl mx-auto px-6 py-20
">
  {features.map((feature, index) => (
    <div
      key={feature.id}
      className="
        group
        bg-white
        rounded-2xl
        p-8
        border border-neutral-200 hover:border-primary-300
        shadow-md hover:shadow-xl
        transform hover:-translate-y-2
        transition-all duration-300 ease-out
        animate-slideUp
      "
      style={{ animationDelay: `${index * 100}ms` }}
    >
      <div className="
        w-14 h-14
        bg-primary-100 group-hover:bg-primary-600
        text-primary-600 group-hover:text-white
        rounded-xl
        flex items-center justify-center
        transform group-hover:scale-110 group-hover:rotate-3
        transition-all duration-300
      ">
        <feature.Icon className="w-7 h-7" />
      </div>

      <h3 className="
        mt-6 text-xl font-semibold text-neutral-900
      ">
        {feature.title}
      </h3>

      <p className="
        mt-3 text-neutral-600 leading-relaxed
      ">
        {feature.description}
      </p>
    </div>
  ))}
</div>
```

#### CTA Section
```tsx
<section className="
  bg-gradient-to-r from-primary-600 to-accent-600
  py-20 px-6
  text-center
  relative overflow-hidden
">
  <div className="relative z-10 container max-w-4xl mx-auto">
    <h2 className="
      text-4xl md:text-5xl font-bold text-white
      leading-tight
    ">
      Ready to Get Organized?
    </h2>

    <p className="mt-4 text-xl text-primary-100">
      Join thousands of productive users today.
    </p>

    <button className="
      mt-8 px-10 py-4
      bg-white hover:bg-neutral-100
      text-primary-600 text-lg font-bold tracking-wide
      rounded-xl
      shadow-2xl hover:shadow-[0_20px_60px_rgba(0,0,0,0.3)]
      transform hover:scale-110 active:scale-95
      transition-all duration-300 ease-out
    ">
      Start Free Trial
    </button>
  </div>

  {/* Background decoration */}
  <div className="
    absolute top-0 left-0 right-0 bottom-0
    opacity-10
  ">
    {/* SVG pattern or gradient mesh */}
  </div>
</section>
```

---

### Auth Pages (Sign-in / Sign-up)

#### Centered Card Layout
```tsx
<div className="
  min-h-screen
  flex items-center justify-center
  bg-gradient-to-br from-neutral-50 to-neutral-100
  p-4
">
  <div className="
    w-full max-w-md
    bg-white
    rounded-2xl
    shadow-2xl
    border border-neutral-200
    overflow-hidden
    animate-slideUp
  ">
    {/* Logo/Header */}
    <div className="
      px-8 pt-8 pb-6
      text-center
      border-b border-neutral-200
    ">
      <h1 className="
        text-3xl font-bold text-neutral-900
      ">
        Welcome Back
      </h1>
      <p className="mt-2 text-neutral-600">
        Sign in to continue to your tasks
      </p>
    </div>

    {/* Form */}
    <form className="p-8 space-y-6">
      {/* Email input with floating label (see Input section) */}

      {/* Password input with show/hide toggle */}

      {/* Remember me + Forgot password */}
      <div className="flex items-center justify-between">
        <label className="flex items-center gap-2">
          <input type="checkbox" className="..." />
          <span className="text-sm text-neutral-600">Remember me</span>
        </label>

        <a href="#" className="
          text-sm text-primary-600 hover:text-primary-700
          font-medium
          hover:underline
        ">
          Forgot password?
        </a>
      </div>

      {/* Submit button */}
      <button type="submit" className="
        w-full px-6 py-3
        bg-primary-600 hover:bg-primary-700 active:bg-primary-800
        text-white font-semibold text-lg tracking-wide
        rounded-lg
        shadow-md hover:shadow-lg
        transform hover:scale-[1.02] active:scale-[0.98]
        transition-all duration-200 ease-out
        focus:outline-none focus:ring-4 focus:ring-primary-200
      ">
        Sign In
      </button>

      {/* Divider */}
      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-neutral-300" />
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="px-4 bg-white text-neutral-500">
            Or continue with
          </span>
        </div>
      </div>

      {/* Social login buttons */}
      <div className="grid grid-cols-2 gap-4">
        <button className="
          px-4 py-2.5
          bg-white hover:bg-neutral-50
          text-neutral-700 font-medium
          border-2 border-neutral-300 hover:border-neutral-400
          rounded-lg
          flex items-center justify-center gap-2
          transition-all duration-200
          focus:outline-none focus:ring-2 focus:ring-neutral-300
        ">
          <GoogleIcon className="w-5 h-5" />
          <span>Google</span>
        </button>

        <button className="
          px-4 py-2.5
          bg-white hover:bg-neutral-50
          text-neutral-700 font-medium
          border-2 border-neutral-300 hover:border-neutral-400
          rounded-lg
          flex items-center justify-center gap-2
          transition-all duration-200
          focus:outline-none focus:ring-2 focus:ring-neutral-300
        ">
          <GithubIcon className="w-5 h-5" />
          <span>GitHub</span>
        </button>
      </div>
    </form>

    {/* Footer */}
    <div className="
      px-8 py-6
      bg-neutral-50
      text-center
      border-t border-neutral-200
    ">
      <p className="text-sm text-neutral-600">
        Don't have an account?{' '}
        <a href="/signup" className="
          text-primary-600 hover:text-primary-700
          font-semibold
          hover:underline
        ">
          Sign up free
        </a>
      </p>
    </div>
  </div>
</div>
```

#### Password Strength Indicator
```tsx
<div className="mt-2">
  <div className="flex gap-1">
    {[1, 2, 3, 4].map((level) => (
      <div
        key={level}
        className={`
          h-1 flex-1 rounded-full
          transition-all duration-300
          ${strength >= level
            ? strength === 1 ? 'bg-error-500'
            : strength === 2 ? 'bg-warning-500'
            : strength === 3 ? 'bg-info-500'
            : 'bg-success-500'
            : 'bg-neutral-300'
          }
        `}
      />
    ))}
  </div>
  <p className="mt-1.5 text-xs text-neutral-600">
    {strengthText}
  </p>
</div>
```

#### Error Shake Animation
```tsx
// When form validation fails:
<form className={`
  ${hasError ? 'animate-shake' : ''}
`}>
  {/* Form fields */}
</form>
```

---

### Main App (Todo Interface)

#### Layout Structure
```tsx
<div className="min-h-screen bg-neutral-50">
  {/* Sticky navbar */}
  <nav className="
    sticky top-0 z-50
    bg-white/90 backdrop-blur-md
    border-b border-neutral-200
    shadow-sm
  ">
    {/* Nav content */}
  </nav>

  {/* Main content area */}
  <div className="flex">
    {/* Sidebar (collapsible) */}
    <aside className={`
      ${sidebarOpen ? 'w-64' : 'w-0'}
      bg-white
      border-r border-neutral-200
      transition-all duration-300 ease-out
      overflow-hidden
    `}>
      {/* Sidebar content */}
    </aside>

    {/* Main todo area */}
    <main className="flex-1 p-6 md:p-8">
      {/* Todo content */}
    </main>
  </div>
</div>
```

#### Add Task Input (Floating)
```tsx
<div className="
  sticky top-20 z-40
  bg-white
  rounded-xl
  shadow-lg
  border-2 border-primary-300
  p-4
  animate-slideDown
">
  <input
    type="text"
    placeholder="What needs to be done?"
    className="
      w-full px-4 py-3
      bg-transparent
      text-lg text-neutral-900 placeholder:text-neutral-400
      focus:outline-none
    "
  />

  <div className="mt-3 flex items-center justify-between">
    <div className="flex gap-2">
      <button className="
        p-2 rounded-lg
        text-neutral-500 hover:text-neutral-900 hover:bg-neutral-100
        transition-colors
      " title="Add due date">
        <CalendarIcon className="w-5 h-5" />
      </button>

      <button className="
        p-2 rounded-lg
        text-neutral-500 hover:text-neutral-900 hover:bg-neutral-100
        transition-colors
      " title="Set priority">
        <FlagIcon className="w-5 h-5" />
      </button>
    </div>

    <button className="
      px-5 py-2
      bg-primary-600 hover:bg-primary-700
      text-white font-semibold
      rounded-lg
      transform hover:scale-105 active:scale-95
      transition-all duration-200
    ">
      Add
    </button>
  </div>
</div>
```

#### Todo Item
```tsx
<div className={`
  group
  bg-white
  rounded-lg
  p-4
  border border-neutral-200 hover:border-neutral-300
  shadow-sm hover:shadow-md
  transition-all duration-200
  ${completed ? 'opacity-60' : ''}
  animate-slideDown
`}>
  <div className="flex items-start gap-3">
    {/* Custom checkbox */}
    <label className="flex-shrink-0 mt-0.5">
      <input
        type="checkbox"
        checked={completed}
        className="sr-only peer"
      />
      <div className="
        w-6 h-6
        bg-white border-2 border-neutral-400
        peer-checked:bg-primary-600 peer-checked:border-primary-600
        rounded-full
        transition-all duration-300
        cursor-pointer
        flex items-center justify-center
      ">
        <svg
          className={`
            w-4 h-4 text-white
            transition-all duration-300
            ${completed
              ? 'scale-100 opacity-100'
              : 'scale-0 opacity-0'
            }
          `}
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"/>
        </svg>
      </div>
    </label>

    {/* Task text */}
    <div className="flex-1 min-w-0">
      <p className={`
        text-neutral-900 font-medium
        relative
        after:absolute after:left-0 after:top-1/2 after:h-0.5
        after:bg-neutral-900 after:transition-all after:duration-500
        ${completed ? 'after:w-full' : 'after:w-0'}
      `}>
        Finish project documentation
      </p>

      <div className="mt-2 flex items-center gap-3 text-sm text-neutral-500">
        <span className="flex items-center gap-1">
          <CalendarIcon className="w-4 h-4" />
          Today
        </span>

        <span className="
          px-2 py-0.5
          bg-error-100 text-error-700
          text-xs font-semibold uppercase tracking-wide
          rounded-full
        ">
          High
        </span>
      </div>
    </div>

    {/* Actions (visible on hover) */}
    <div className="
      flex gap-1
      opacity-0 group-hover:opacity-100
      transition-opacity duration-200
    ">
      <button className="
        p-2 rounded-lg
        text-neutral-500 hover:text-primary-600 hover:bg-primary-50
        transition-colors
      ">
        <EditIcon className="w-4 h-4" />
      </button>

      <button className="
        p-2 rounded-lg
        text-neutral-500 hover:text-error-600 hover:bg-error-50
        transition-colors
      ">
        <TrashIcon className="w-4 h-4" />
      </button>
    </div>
  </div>
</div>
```

#### Delete Animation Implementation
```tsx
const [removing, setRemoving] = useState(false);

const handleDelete = async (id: string) => {
  setRemoving(true);

  // Wait for animation to complete
  setTimeout(async () => {
    await deleteTodo(id);
    // Remove from state/UI
  }, 300);
};

<div className={`
  transition-all duration-300 ease-in
  ${removing
    ? 'translate-x-full opacity-0'
    : 'translate-x-0 opacity-100'
  }
`}>
  {/* Todo item */}
</div>
```

#### Empty State
```tsx
<div className="
  flex flex-col items-center justify-center
  py-20
  text-center
  animate-fadeIn
">
  <div className="
    w-24 h-24
    bg-neutral-100
    rounded-full
    flex items-center justify-center
    mb-6
  ">
    <CheckCircleIcon className="w-12 h-12 text-neutral-400" />
  </div>

  <h3 className="text-2xl font-semibold text-neutral-900">
    All caught up!
  </h3>

  <p className="mt-2 text-neutral-600 max-w-sm">
    No tasks for today. Add a new task to get started.
  </p>

  <button className="
    mt-6 px-6 py-3
    bg-primary-600 hover:bg-primary-700
    text-white font-semibold
    rounded-lg
    shadow-md hover:shadow-lg
    transform hover:scale-105
    transition-all duration-200
  ">
    Add Your First Task
  </button>
</div>
```

#### Progress Indicator (Circular)
```tsx
<div className="relative w-32 h-32">
  <svg className="w-full h-full -rotate-90">
    {/* Background circle */}
    <circle
      cx="64"
      cy="64"
      r="56"
      stroke="currentColor"
      strokeWidth="8"
      fill="none"
      className="text-neutral-200"
    />

    {/* Progress circle */}
    <circle
      cx="64"
      cy="64"
      r="56"
      stroke="currentColor"
      strokeWidth="8"
      fill="none"
      strokeDasharray={`${2 * Math.PI * 56}`}
      strokeDashoffset={`${2 * Math.PI * 56 * (1 - progress / 100)}`}
      className="text-primary-600 transition-all duration-500 ease-out"
      strokeLinecap="round"
    />
  </svg>

  {/* Center text */}
  <div className="
    absolute inset-0
    flex flex-col items-center justify-center
  ">
    <span className="text-3xl font-bold text-neutral-900">
      {progress}%
    </span>
    <span className="text-sm text-neutral-600">
      Complete
    </span>
  </div>
</div>
```

#### Drag and Drop Visual Feedback
```tsx
// While dragging:
className="
  opacity-50
  scale-95
  rotate-2
  shadow-2xl
  cursor-grabbing
  transition-all duration-150
"

// Drop zone (when drag over):
className="
  border-2 border-dashed border-primary-500
  bg-primary-50
  transition-all duration-150
"
```

---

## Code Implementation Notes

### Global CSS Setup

Create `app/globals.css`:

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    /* Color variables (light mode) */
    --primary-50: #f0f9ff;
    --primary-500: #0ea5e9;
    --primary-600: #0284c7;
    --primary-700: #0369a1;

    /* ... rest of colors */

    --bg-main: #ffffff;
    --bg-card: #ffffff;
  }

  [data-theme="dark"] {
    --bg-main: #0a0a0a;
    --bg-card: #171717;
    /* ... dark mode overrides */
  }

  * {
    @apply border-neutral-300;
  }

  body {
    @apply bg-[var(--bg-main)] text-neutral-900 font-normal;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  }

  h1, h2, h3, h4, h5, h6 {
    @apply font-semibold text-neutral-900;
  }
}

@layer utilities {
  .text-balance {
    text-wrap: balance;
  }

  .scrollbar-hide {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }

  .scrollbar-hide::-webkit-scrollbar {
    display: none;
  }
}

/* Smooth scrolling */
html {
  scroll-behavior: smooth;
}

/* Respect reduced motion preference */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}

/* Focus visible styles */
*:focus-visible {
  @apply outline-none ring-4 ring-primary-200 ring-offset-2;
}
```

---

### Complete Tailwind Config

Update `tailwind.config.ts`:

```typescript
import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: ['class', '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        // Primary palette
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },

        // Accent palette
        accent: {
          50: '#fdf4ff',
          100: '#fae8ff',
          200: '#f5d0fe',
          300: '#f0abfc',
          400: '#e879f9',
          500: '#d946ef',
          600: '#c026d3',
          700: '#a21caf',
          800: '#86198f',
          900: '#701a75',
        },

        // Semantic colors
        success: {
          50: '#f0fdf4',
          100: '#dcfce7',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
        },

        warning: {
          50: '#fffbeb',
          100: '#fef3c7',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
        },

        error: {
          50: '#fef2f2',
          100: '#fee2e2',
          500: '#ef4444',
          600: '#dc2626',
          700: '#b91c1c',
        },

        info: {
          50: '#eff6ff',
          100: '#dbeafe',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },

        // Neutral scale
        neutral: {
          50: '#fafafa',
          100: '#f5f5f5',
          200: '#e5e5e5',
          300: '#d4d4d4',
          400: '#a3a3a3',
          500: '#737373',
          600: '#525252',
          700: '#404040',
          800: '#262626',
          900: '#171717',
          950: '#0a0a0a',
        },

        // Semantic aliases
        background: 'var(--bg-main)',
        foreground: 'var(--foreground)',
      },

      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },

      fontSize: {
        xs: ['0.75rem', { lineHeight: '1rem' }],
        sm: ['0.875rem', { lineHeight: '1.25rem' }],
        base: ['1rem', { lineHeight: '1.5rem' }],
        lg: ['1.125rem', { lineHeight: '1.75rem' }],
        xl: ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
        '5xl': ['3rem', { lineHeight: '1' }],
      },

      boxShadow: {
        'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'DEFAULT': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)',
        'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
        'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)',
        'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)',
        '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
      },

      animation: {
        // Fade
        'fadeIn': 'fadeIn 400ms ease-out',
        'fadeOut': 'fadeOut 300ms ease-in',

        // Slide
        'slideUp': 'slideUp 400ms ease-out',
        'slideDown': 'slideDown 400ms ease-out',
        'slideInRight': 'slideInRight 300ms ease-out',
        'slideInLeft': 'slideInLeft 300ms ease-out',
        'slideOutRight': 'slideOutRight 300ms ease-in',

        // Scale
        'scaleIn': 'scaleIn 200ms ease-out',
        'scaleOut': 'scaleOut 200ms ease-in',

        // Special
        'shimmer': 'shimmer 2s infinite',
        'pulse-soft': 'pulseSoft 2s ease-in-out infinite',
        'bounce-soft': 'bounceSoft 1s ease-in-out',
        'shake': 'shake 400ms ease-in-out',

        // Loading
        'spin-slow': 'spin 1.5s linear infinite',
        'ping-slow': 'ping 2s cubic-bezier(0, 0, 0.2, 1) infinite',
      },

      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeOut: {
          '0%': { opacity: '1' },
          '100%': { opacity: '0' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideInRight: {
          '0%': { transform: 'translateX(100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        slideInLeft: {
          '0%': { transform: 'translateX(-100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        slideOutRight: {
          '0%': { transform: 'translateX(0)', opacity: '1' },
          '100%': { transform: 'translateX(100%)', opacity: '0' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.9)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        scaleOut: {
          '0%': { transform: 'scale(1)', opacity: '1' },
          '100%': { transform: 'scale(0.9)', opacity: '0' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-1000px 0' },
          '100%': { backgroundPosition: '1000px 0' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
        bounceSoft: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        shake: {
          '0%, 100%': { transform: 'translateX(0)' },
          '10%, 30%, 50%, 70%, 90%': { transform: 'translateX(-4px)' },
          '20%, 40%, 60%, 80%': { transform: 'translateX(4px)' },
        },
      },

      transitionTimingFunction: {
        'bounce': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
        'spring': 'cubic-bezier(0.175, 0.885, 0.32, 1.275)',
      },
    },
  },
  plugins: [],
};

export default config;
```

---

## Example Component Library

### Button Component (`components/ui/Button.tsx`)

```typescript
import { ButtonHTMLAttributes, ReactNode } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  children: ReactNode;
  isLoading?: boolean;
}

export default function Button({
  variant = 'primary',
  size = 'md',
  children,
  isLoading = false,
  disabled,
  className = '',
  ...props
}: ButtonProps) {
  const baseStyles = `
    inline-flex items-center justify-center gap-2
    font-semibold tracking-wide
    rounded-lg
    transform transition-all duration-200 ease-out
    focus:outline-none
    disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none
  `;

  const variants = {
    primary: `
      bg-primary-600 hover:bg-primary-700 active:bg-primary-800
      text-white
      shadow-md hover:shadow-lg
      hover:scale-[1.02] active:scale-[0.98]
      focus:ring-4 focus:ring-primary-200
    `,
    secondary: `
      bg-transparent hover:bg-neutral-100 active:bg-neutral-200
      text-primary-600 hover:text-primary-700
      border-2 border-primary-600 hover:border-primary-700
      hover:scale-[1.02] active:scale-[0.98]
      focus:ring-4 focus:ring-primary-200
    `,
    ghost: `
      bg-transparent hover:bg-neutral-100 active:bg-neutral-200
      text-neutral-700 hover:text-neutral-900
      focus:ring-2 focus:ring-neutral-300
    `,
    danger: `
      bg-error-600 hover:bg-error-700 active:bg-error-800
      text-white
      shadow-md hover:shadow-lg
      hover:scale-[1.02] active:scale-[0.98]
      focus:ring-4 focus:ring-error-200
    `,
  };

  const sizes = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-2.5 text-base',
    lg: 'px-8 py-3 text-lg',
  };

  return (
    <button
      className={`
        ${baseStyles}
        ${variants[variant]}
        ${sizes[size]}
        ${className}
      `}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <>
          <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
          <span>Loading...</span>
        </>
      ) : (
        children
      )}
    </button>
  );
}
```

### Input Component (`components/ui/Input.tsx`)

```typescript
import { InputHTMLAttributes, forwardRef } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, className = '', id, ...props }, ref) => {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, '-');

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={inputId}
            className="block mb-2 text-sm font-medium text-neutral-700"
          >
            {label}
          </label>
        )}

        <input
          ref={ref}
          id={inputId}
          className={`
            w-full px-4 py-2.5
            bg-white border-2
            rounded-lg
            transition-all duration-200 ease-out
            focus:outline-none
            disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-neutral-100
            ${error
              ? 'border-error-500 bg-error-50 focus:border-error-600 focus:ring-4 focus:ring-error-100'
              : 'border-neutral-300 focus:border-primary-500 focus:ring-4 focus:ring-primary-100 hover:border-neutral-400'
            }
            ${className}
          `}
          {...props}
        />

        {error && (
          <p className="mt-1.5 text-sm text-error-600 flex items-center gap-1">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <span>{error}</span>
          </p>
        )}

        {helperText && !error && (
          <p className="mt-1.5 text-sm text-neutral-600">
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input;
```

### Card Component (`components/ui/Card.tsx`)

```typescript
import { HTMLAttributes, ReactNode } from 'react';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  hoverable?: boolean;
  elevated?: boolean;
}

export default function Card({
  children,
  hoverable = false,
  elevated = false,
  className = '',
  ...props
}: CardProps) {
  const baseStyles = `
    bg-white
    rounded-xl
    border border-neutral-200
    overflow-hidden
  `;

  const hoverStyles = hoverable ? `
    shadow-md hover:shadow-xl
    hover:border-neutral-300
    transform hover:-translate-y-2
    transition-all duration-300 ease-out
    cursor-pointer
  ` : 'shadow-sm';

  const elevatedStyles = elevated ? 'shadow-2xl' : '';

  return (
    <div
      className={`
        ${baseStyles}
        ${hoverStyles}
        ${elevatedStyles}
        ${className}
      `}
      {...props}
    >
      {children}
    </div>
  );
}
```

---

## Usage Guidelines Summary

### DO:
- Use the defined color palette consistently
- Apply animations to enhance UX (loading states, feedback)
- Ensure all text meets AAA contrast ratios
- Use the spacing scale (4px base) for all margins/padding
- Respect `prefers-reduced-motion`
- Keep animations GPU-accelerated (transform, opacity)
- Use semantic HTML elements
- Provide focus states for keyboard navigation

### DON'T:
- Invent new colors outside the palette
- Add animations just for decoration
- Use low-contrast color combinations
- Use arbitrary pixel values (stick to the scale)
- Ignore accessibility requirements
- Animate expensive properties (width, height, top, left)
- Use divs for buttons or links
- Forget hover and focus states

---

## Maintenance & Updates

**Version History:**
- v1.0.0 (2025-12-21): Initial design system

**Review Schedule:**
- Monthly: Check for consistency across new features
- Quarterly: Review and update color palette if needed
- Annually: Major version update with user feedback

**Feedback:**
When implementing this design system, note any inconsistencies or missing patterns and update this document accordingly.

---

**End of UI Design System Skill**

This skill should be referenced whenever building or updating any page in the Todo app to ensure consistent, professional, and delightful user experiences.

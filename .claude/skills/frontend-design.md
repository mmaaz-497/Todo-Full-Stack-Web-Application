---
name: frontend-design
description: Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web components, pages, or applications. Generates creative, polished code that avoids generic AI aesthetics.
license: Complete terms in LICENSE.txt
---

# Frontend Design Skill

## Purpose & Scope

This skill produces **exceptional, memorable frontend interfaces** that combine technical excellence with artistic vision. Use this skill when building web components, pages, or complete applications that need to stand out from generic AI-generated designs.

**Primary Goal**: Create interfaces users remember—not because they're flashy, but because they're intentional, polished, and distinctly human-crafted.

**Scope**:
- UI component architecture and implementation
- Design system creation and application
- Motion design and micro-interactions
- Accessibility compliance (WCAG 2.1 AA)
- Performance optimization
- Responsive and adaptive layouts
- Typography and color systems
- State management and loading patterns

**Out of Scope**:
- Backend API design
- Database architecture
- Authentication logic (UI only)
- SEO strategy (implementation only)

## Design Thinking Process

Before writing any code, complete this mental model:

### 1. Define Purpose (The "Why")
Ask and answer:
- **Who is this for?** (audience persona, context, device)
- **What problem does this solve?** (user pain point, goal)
- **What action should they take?** (primary CTA, success state)
- **What should they feel?** (emotional response: trust, excitement, calm)

### 2. Choose Aesthetic Direction (The "How")
Select **ONE** design language and commit fully:

**Brutalist**
- Raw, structural honesty
- High contrast (black/white or bold colors)
- Exposed grids, borders, and structure
- Monospace or grotesque fonts
- Minimal decoration, maximal function
- Example vibe: Architectural blueprints, punk zines

**Editorial**
- Typography as hero element
- Magazine-inspired layouts
- Generous white space
- Serif + sans pairings
- Sophisticated hierarchy
- Example vibe: Print magazines, literary journals

**Cinematic**
- Immersive, layered environments
- Depth through shadows and gradients
- Atmospheric effects (grain, blur, overlays)
- Dramatic lighting
- Rich, saturated colors
- Example vibe: Film posters, video games

**Luxury**
- Refined elegance and restraint
- Premium materials (gold accents, subtle textures)
- Spacious layouts with breathing room
- Serif typography
- Muted, sophisticated color palettes
- Example vibe: High-end brands, jewelry sites

**Retro-Futuristic**
- Nostalgic tech aesthetics (80s/90s/Y2K)
- Vibrant gradients and neon
- Geometric shapes
- Pixelated or tech-inspired fonts
- Glitch effects (tasteful)
- Example vibe: Synthwave, cyberpunk

**Experimental**
- Unconventional layouts
- Playful, boundary-pushing interactions
- Asymmetry and surprise
- Custom cursors, scroll effects
- Bold type and color
- Example vibe: Art portfolios, creative studios

**Minimalist (Refined)**
- Essential elements only
- Precise alignment and spacing
- Intentional use of negative space
- Restrained color (1-2 accent colors)
- Clean sans-serif typography
- Example vibe: Apple, Muji, Dieter Rams

### 3. Establish Design System Tokens
Before coding, define:

**Typography Scale**
```typescript
const typeScale = {
  xs: '0.75rem',    // 12px - captions
  sm: '0.875rem',   // 14px - small text
  base: '1rem',     // 16px - body
  lg: '1.125rem',   // 18px - large body
  xl: '1.25rem',    // 20px - subheadings
  '2xl': '1.5rem',  // 24px - headings
  '3xl': '1.875rem', // 30px - large headings
  '4xl': '2.25rem',  // 36px - hero text
  '5xl': '3rem',     // 48px - display
  '6xl': '3.75rem'   // 60px - hero display
};
```

**Spacing Rhythm** (8px base unit)
```typescript
const spacing = {
  0: '0',
  1: '0.25rem',  // 4px
  2: '0.5rem',   // 8px - base unit
  3: '0.75rem',  // 12px
  4: '1rem',     // 16px
  6: '1.5rem',   // 24px
  8: '2rem',     // 32px
  12: '3rem',    // 48px
  16: '4rem',    // 64px
  24: '6rem',    // 96px
  32: '8rem'     // 128px
};
```

**Motion System**
```typescript
const motion = {
  duration: {
    instant: '100ms',
    fast: '200ms',
    base: '300ms',
    slow: '500ms',
    slower: '700ms'
  },
  easing: {
    linear: 'linear',
    easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
    easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
    easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    spring: 'cubic-bezier(0.34, 1.56, 0.64, 1)'
  }
};
```

### 4. Architect Component Hierarchy
Plan composition strategy:
```
Layout Components (structural)
├── Page Shell
├── Grid Systems
└── Container Wrappers

Primitive Components (foundational)
├── Button
├── Input
├── Card
└── Badge

Composite Components (assembled)
├── TaskCard (Card + Button + Badge)
├── TaskList (Grid + TaskCard[])
└── Dashboard (Page + TaskList + Header)
```

## Aesthetic Commitment Rules

### Typography: The Foundation

**FORBIDDEN FONTS** (generic, overused):
- ❌ Inter
- ❌ Roboto
- ❌ Arial, Helvetica
- ❌ System font stack alone
- ❌ Single-font designs

**RECOMMENDED PAIRINGS**:

*Modern Sans + Serif*
- **Space Grotesk** (headings) + **Fraunces** (body)
- **Syne** (headings) + **Crimson Pro** (body)
- **Cabinet Grotesk** (headings) + **Newsreader** (body)

*Geometric Sans + Humanist Sans*
- **Outfit** (headings) + **Plus Jakarta Sans** (body)
- **Archivo** (headings) + **Manrope** (body)

*Display + Readable Sans*
- **Instrument Sans** (headings) + **DM Sans** (body)
- **Schibsted Grotesk** (headings) + **IBM Plex Sans** (body)

**Typography Rules**:
1. Establish clear hierarchy (6+ levels)
2. Use consistent scale (modular scale recommended)
3. Set line-height for readability (1.5-1.7 for body, 1.2-1.3 for headings)
4. Optimize font loading (next/font with display: 'swap')
5. Use optical sizing when available
6. Apply proper tracking/letter-spacing
7. Ensure 60-75 characters per line for readability

**Implementation**:
```typescript
// app/layout.tsx
import { Space_Grotesk, Fraunces } from 'next/font/google';

const spaceGrotesk = Space_Grotesk({
  subsets: ['latin'],
  variable: '--font-sans',
  display: 'swap',
  weight: ['300', '400', '500', '600', '700']
});

const fraunces = Fraunces({
  subsets: ['latin'],
  variable: '--font-serif',
  display: 'swap',
  axes: ['SOFT', 'WONK'],
  weight: ['400', '500', '600', '700']
});

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={`${spaceGrotesk.variable} ${fraunces.variable}`}>
      <body className="font-sans">{children}</body>
    </html>
  );
}
```

```css
/* globals.css */
@layer base {
  :root {
    --font-sans: var(--font-space-grotesk);
    --font-serif: var(--font-fraunces);
  }

  h1, h2, h3, h4, h5, h6 {
    font-family: var(--font-serif);
    font-weight: 600;
    line-height: 1.2;
    letter-spacing: -0.02em;
  }

  p, span, div {
    font-family: var(--font-sans);
    line-height: 1.6;
  }
}
```

### Color & Theme Strategy

**FORBIDDEN**:
- ❌ Purple-on-white gradients
- ❌ Default Tailwind gray scale (gray-50 through gray-950)
- ❌ Random color choices without system
- ❌ Poor contrast ratios

**REQUIRED**:
- ✅ Intentional palette (5-7 core colors)
- ✅ HSL color space (easier manipulation)
- ✅ CSS custom properties
- ✅ Semantic naming (not color-based)
- ✅ Accessible contrast (4.5:1 text, 3:1 UI)
- ✅ Dark mode consideration

**Color System Structure**:
```css
@layer base {
  :root {
    /* Semantic colors (HSL for manipulation) */
    --color-primary: 220 90% 56%;     /* Brand blue */
    --color-secondary: 280 60% 60%;   /* Accent purple */
    --color-success: 142 76% 36%;     /* Green */
    --color-warning: 38 92% 50%;      /* Amber */
    --color-danger: 0 84% 60%;        /* Red */

    /* Neutral scale (custom, not default Tailwind) */
    --color-surface-50: 0 0% 98%;
    --color-surface-100: 0 0% 96%;
    --color-surface-200: 0 0% 90%;
    --color-surface-300: 0 0% 83%;
    --color-surface-800: 222 47% 11%;
    --color-surface-900: 222 47% 7%;
    --color-surface-950: 222 47% 4%;

    /* Text colors */
    --color-text-primary: var(--color-surface-950);
    --color-text-secondary: var(--color-surface-800);
    --color-text-tertiary: var(--color-surface-600);

    /* Surface colors */
    --color-background: var(--color-surface-50);
    --color-foreground: var(--color-surface-950);
  }

  [data-theme="dark"] {
    --color-background: var(--color-surface-950);
    --color-foreground: var(--color-surface-50);
    --color-text-primary: var(--color-surface-50);
    --color-text-secondary: var(--color-surface-200);
  }
}
```

**Usage in Tailwind**:
```typescript
// tailwind.config.ts
export default {
  theme: {
    extend: {
      colors: {
        primary: 'hsl(var(--color-primary) / <alpha-value>)',
        secondary: 'hsl(var(--color-secondary) / <alpha-value>)',
        surface: {
          50: 'hsl(var(--color-surface-50) / <alpha-value>)',
          // ... other shades
        },
        text: {
          primary: 'hsl(var(--color-text-primary) / <alpha-value>)',
          secondary: 'hsl(var(--color-text-secondary) / <alpha-value>)'
        }
      }
    }
  }
};
```

### Motion & Interaction Strategy

**Philosophy**: Motion should clarify, guide, and delight—never distract.

**Motion Principles**:
1. **Purposeful**: Every animation has a reason (feedback, transition, attention)
2. **Natural**: Physics-inspired easing (not linear)
3. **Coordinated**: Related elements move together with stagger
4. **Respectful**: Honor prefers-reduced-motion
5. **Performant**: Use transform and opacity only (avoid layout triggers)

**Easing Curves**:
```css
:root {
  /* Standard curves */
  --ease-linear: linear;
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);

  /* Custom curves */
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);      /* Bouncy */
  --ease-smooth: cubic-bezier(0.65, 0, 0.35, 1);        /* Refined */
  --ease-dramatic: cubic-bezier(0.87, 0, 0.13, 1);      /* Cinematic */
}
```

**Duration Scale**:
- **100ms**: Instant feedback (hover states)
- **200ms**: Fast transitions (tooltips, dropdowns)
- **300ms**: Standard transitions (modals, slides)
- **500ms**: Slow transitions (page changes)
- **700ms+**: Dramatic effects (hero animations)

**Animation Patterns**:

*Fade In*
```typescript
// Framer Motion
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  transition={{ duration: 0.3, ease: [0.65, 0, 0.35, 1] }}
>
  Content
</motion.div>
```

*Slide Up*
```typescript
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.4, ease: [0.65, 0, 0.35, 1] }}
>
  Content
</motion.div>
```

*Stagger Children*
```typescript
<motion.ul
  initial="hidden"
  animate="visible"
  variants={{
    visible: {
      transition: { staggerChildren: 0.05 }
    }
  }}
>
  {items.map(item => (
    <motion.li
      key={item.id}
      variants={{
        hidden: { opacity: 0, y: 20 },
        visible: { opacity: 1, y: 0 }
      }}
    >
      {item.title}
    </motion.li>
  ))}
</motion.ul>
```

*Hover Interactions*
```typescript
<motion.button
  whileHover={{ scale: 1.02, y: -2 }}
  whileTap={{ scale: 0.98 }}
  transition={{ duration: 0.2 }}
  className="rounded-lg bg-primary px-6 py-3 text-white"
>
  Click Me
</motion.button>
```

**Respect Reduced Motion**:
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

### Layout & Spatial Composition

**Grid Systems**: Use intentional grids, not arbitrary containers.

**12-Column Grid**:
```typescript
<div className="grid grid-cols-12 gap-6">
  <div className="col-span-12 md:col-span-8">Main content</div>
  <div className="col-span-12 md:col-span-4">Sidebar</div>
</div>
```

**Asymmetric Layouts** (more interesting):
```typescript
<div className="grid grid-cols-12 gap-8">
  <div className="col-span-12 md:col-span-7">Featured</div>
  <div className="col-span-12 md:col-span-5">Secondary</div>
</div>
```

**Vertical Rhythm**: Consistent spacing multiples.
```typescript
// Use spacing scale: 4, 8, 12, 16, 24, 32, 48, 64, 96
<div className="space-y-8"> {/* 32px between items */}
  <section className="space-y-4"> {/* 16px within section */}
    <h2>Title</h2>
    <p>Content</p>
  </section>
</div>
```

**Container Strategies**:
```typescript
// Generic (avoid)
<div className="mx-auto max-w-7xl px-4">

// Intentional (preferred)
<div className="mx-auto max-w-prose px-6">      {/* ~65ch for text */}
<div className="mx-auto max-w-5xl px-8">        {/* ~1024px for content */}
<div className="mx-auto max-w-screen-2xl px-12"> {/* ~1536px for wide layouts */}
```

## Next.js App Router Best Practices

### Server vs. Client Components

**Default to Server Components** (better performance):
```typescript
// app/page.tsx - Server Component (default)
export default async function Page() {
  const data = await fetchData(); // Can fetch directly
  return (
    <main>
      <StaticContent data={data} />
    </main>
  );
}
```

**Use Client Components only when needed**:
```typescript
'use client'; // Explicit opt-in

import { useState } from 'react';

export function InteractiveButton() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```

**Composition Pattern** (Server wraps Client):
```typescript
// app/page.tsx (Server)
import { ClientWidget } from './client-widget';

export default function Page() {
  return (
    <main>
      <h1>Server-rendered heading</h1>
      <ClientWidget /> {/* Client interactivity */}
    </main>
  );
}
```

### Image Optimization

**Always use next/image**:
```typescript
import Image from 'next/image';

<Image
  src="/hero.jpg"
  alt="Descriptive alternative text"
  width={1200}
  height={800}
  priority // for above-fold images
  placeholder="blur" // or blurDataURL for better UX
  className="rounded-2xl"
/>
```

**Responsive Images**:
```typescript
<Image
  src="/hero.jpg"
  alt="Hero image"
  fill
  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
  className="object-cover"
/>
```

### Font Optimization

**Use next/font for zero layout shift**:
```typescript
import { Space_Grotesk } from 'next/font/google';

const spaceGrotesk = Space_Grotesk({
  subsets: ['latin'],
  variable: '--font-sans',
  display: 'swap', // Avoid FOIT
  preload: true,
  fallback: ['system-ui', 'sans-serif']
});
```

### Metadata for SEO

```typescript
// app/page.tsx
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Task Manager - Organize Your Life',
  description: 'A beautiful, intuitive task management app that helps you stay productive.',
  openGraph: {
    title: 'Task Manager',
    description: 'Organize your tasks beautifully',
    images: ['/og-image.jpg'],
  },
  twitter: {
    card: 'summary_large_image',
  }
};
```

## Accessibility Standards

**WCAG 2.1 AA Compliance (Minimum)**:

### Semantic HTML
```typescript
// Good
<nav aria-label="Main navigation">
  <ul>
    <li><a href="/">Home</a></li>
  </ul>
</nav>

<main>
  <h1>Page Title</h1>
  <article>Content</article>
</main>

// Bad
<div className="nav">
  <div className="link">Home</div>
</div>
```

### Keyboard Navigation
```typescript
// All interactive elements must be keyboard accessible
<button
  onClick={handleClick}
  onKeyDown={(e) => e.key === 'Enter' && handleClick()}
  className="..."
>
  Click Me
</button>

// Focus indicators (never remove outline without replacement)
<button className="focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2">
  Accessible Button
</button>
```

### ARIA Labels
```typescript
// Icon buttons need labels
<button aria-label="Close dialog" onClick={onClose}>
  <XIcon />
</button>

// Form inputs need labels
<label htmlFor="email" className="sr-only">Email address</label>
<input id="email" type="email" placeholder="you@example.com" />

// Loading states
<div role="status" aria-live="polite">
  {isLoading ? 'Loading...' : 'Content loaded'}
</div>
```

### Color Contrast
```typescript
// Minimum contrast ratios:
// - Text: 4.5:1
// - Large text (18pt+): 3:1
// - UI components: 3:1

// Check with browser DevTools or online tools
<p className="text-gray-700 bg-white"> {/* ✅ Good contrast */}
  Readable text
</p>

<p className="text-gray-400 bg-white"> {/* ❌ Poor contrast */}
  Hard to read
</p>
```

### Screen Reader Support
```typescript
// Skip links for navigation
<a href="#main-content" className="sr-only focus:not-sr-only">
  Skip to main content
</a>

// Visually hidden but screen reader accessible
<span className="sr-only">Error:</span>
<span className="text-red-600">Invalid email</span>
```

## Performance Rules

### Core Web Vitals Targets
- **LCP** (Largest Contentful Paint): < 2.5s
- **FID** (First Input Delay): < 100ms
- **CLS** (Cumulative Layout Shift): < 0.1

### Optimization Strategies

**1. Image Optimization**
```typescript
// Use next/image, set width/height to prevent CLS
<Image src="/hero.jpg" width={1200} height={800} alt="Hero" priority />
```

**2. Font Loading**
```typescript
// Use next/font with display: 'swap'
const font = Font({ display: 'swap' });
```

**3. Code Splitting**
```typescript
// Dynamic imports for large components
import dynamic from 'next/dynamic';

const HeavyComponent = dynamic(() => import('./heavy-component'), {
  loading: () => <Skeleton />
});
```

**4. Minimize JavaScript**
```typescript
// Prefer Server Components (no JS shipped)
// Use Client Components sparingly
```

**5. Optimize CSS**
```typescript
// Tailwind JIT purges unused styles automatically
// Avoid large CSS-in-JS libraries
```

**6. Lazy Loading**
```typescript
// Images below fold
<Image src="/below-fold.jpg" loading="lazy" />

// Components on interaction
const Modal = dynamic(() => import('./modal'));
```

## Anti-Patterns (Strictly Forbidden)

### Design Anti-Patterns

**❌ Generic SaaS Hero Section**
```typescript
// AVOID
<section className="bg-gradient-to-r from-purple-400 to-pink-600">
  <div className="mx-auto max-w-7xl px-4 py-24 text-center">
    <h1 className="text-5xl font-bold text-white">
      The Best Tool for Your Business
    </h1>
    <button className="mt-8 rounded-full bg-white px-8 py-3">
      Get Started
    </button>
  </div>
</section>
```

**✅ Distinctive Alternative**
```typescript
// PREFERRED
<section className="relative min-h-screen bg-slate-950">
  <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(56,189,248,0.1),transparent_50%)]" />

  <div className="relative mx-auto max-w-6xl px-8 pt-32">
    <h1 className="font-serif text-7xl font-light leading-tight tracking-tight text-slate-50">
      Transform how
      <br />
      <span className="text-sky-400">your team</span> works
    </h1>

    <p className="mt-8 max-w-xl font-sans text-xl text-slate-400">
      A task management system designed for creators who value clarity over clutter.
    </p>

    <button className="group mt-12 rounded-2xl border border-slate-800 bg-slate-900/50 px-8 py-4 backdrop-blur-sm transition-all hover:border-slate-700 hover:bg-slate-900/80">
      <span className="font-sans text-lg text-slate-50 transition-colors group-hover:text-sky-400">
        Start creating
      </span>
    </button>
  </div>
</section>
```

**❌ Boring Card Grid**
```typescript
// AVOID
<div className="grid grid-cols-3 gap-4">
  {items.map(item => (
    <div key={item.id} className="rounded-lg border p-6">
      <h3 className="font-bold">{item.title}</h3>
      <p>{item.description}</p>
    </div>
  ))}
</div>
```

**✅ Elevated Card Grid**
```typescript
// PREFERRED
<div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
  {items.map((item, i) => (
    <motion.article
      key={item.id}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: i * 0.1, duration: 0.5 }}
      className="group relative overflow-hidden rounded-3xl border border-slate-800/50 bg-gradient-to-br from-slate-900/50 to-slate-900/30 p-8 backdrop-blur-sm transition-all hover:border-slate-700 hover:shadow-2xl hover:shadow-sky-500/10"
    >
      <div className="absolute inset-0 bg-gradient-to-br from-sky-500/5 to-transparent opacity-0 transition-opacity group-hover:opacity-100" />

      <h3 className="relative font-serif text-2xl font-semibold text-slate-50">
        {item.title}
      </h3>

      <p className="relative mt-4 font-sans leading-relaxed text-slate-400">
        {item.description}
      </p>

      <div className="relative mt-6 inline-flex items-center gap-2 text-sm font-medium text-sky-400 transition-transform group-hover:translate-x-1">
        Learn more
        <ArrowRightIcon className="h-4 w-4" />
      </div>
    </motion.article>
  ))}
</div>
```

### Technical Anti-Patterns

**❌ Client Component by Default**
```typescript
'use client'; // DON'T do this unless needed

export default function Page() {
  return <div>Static content</div>;
}
```

**❌ Inline Styles**
```typescript
// AVOID
<div style={{ backgroundColor: '#000', padding: '20px' }}>
  Content
</div>

// PREFER
<div className="bg-slate-950 p-5">
  Content
</div>
```

**❌ Missing Alt Text**
```typescript
// AVOID
<img src="/photo.jpg" />

// REQUIRED
<Image src="/photo.jpg" alt="Person working on laptop in café" width={800} height={600} />
```

**❌ No Loading States**
```typescript
// AVOID
return data ? <Content data={data} /> : null;

// PREFER
return data ? <Content data={data} /> : <Skeleton />;
```

## Output Expectations

When implementing a component or page, deliver:

### 1. Complete, Working Code
- TypeScript with proper types
- Next.js App Router patterns
- Tailwind CSS classes
- Framer Motion animations (when appropriate)
- Accessibility attributes

### 2. Design Rationale
Brief explanation of:
- Aesthetic direction chosen
- Typography pairing reasoning
- Color palette intention
- Animation purpose

### 3. Accessibility Notes
- Semantic HTML used
- ARIA labels added
- Keyboard navigation supported
- Color contrast verified

### 4. Performance Optimizations
- Server Components used where possible
- Images optimized with next/image
- Fonts optimized with next/font
- Code splitting applied

### 5. Variants & States
- Default state
- Hover state
- Active/focus state
- Loading state
- Error state
- Empty state
- Disabled state

## Example: Task Card Component

**Full Implementation**:

```typescript
// components/ui/task-card.tsx
'use client';

import { motion } from 'framer-motion';
import { CheckCircleIcon, ClockIcon } from '@heroicons/react/24/outline';
import { CheckCircleIcon as CheckCircleIconSolid } from '@heroicons/react/24/solid';

interface TaskCardProps {
  id: number;
  title: string;
  description?: string;
  completed: boolean;
  dueDate?: string;
  onToggle: (id: number) => void;
  index?: number;
}

export function TaskCard({
  id,
  title,
  description,
  completed,
  dueDate,
  onToggle,
  index = 0
}: TaskCardProps) {
  return (
    <motion.article
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        delay: index * 0.05,
        duration: 0.4,
        ease: [0.65, 0, 0.35, 1]
      }}
      className="group relative"
    >
      <div
        className={`
          relative overflow-hidden rounded-2xl border backdrop-blur-sm transition-all
          ${completed
            ? 'border-emerald-900/50 bg-emerald-950/30'
            : 'border-slate-800/50 bg-slate-900/50 hover:border-slate-700 hover:bg-slate-900/80'
          }
        `}
      >
        {/* Hover gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-br from-sky-500/5 to-transparent opacity-0 transition-opacity group-hover:opacity-100" />

        {/* Content */}
        <div className="relative p-6">
          <div className="flex items-start gap-4">
            {/* Checkbox */}
            <button
              onClick={() => onToggle(id)}
              aria-label={completed ? 'Mark as incomplete' : 'Mark as complete'}
              className="mt-1 flex-shrink-0 transition-transform hover:scale-110 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 focus:ring-offset-slate-950"
            >
              {completed ? (
                <CheckCircleIconSolid className="h-6 w-6 text-emerald-400" />
              ) : (
                <CheckCircleIcon className="h-6 w-6 text-slate-600 transition-colors group-hover:text-slate-400" />
              )}
            </button>

            {/* Text content */}
            <div className="flex-1 min-w-0">
              <h3
                className={`
                  font-sans text-xl transition-colors
                  ${completed
                    ? 'text-slate-500 line-through'
                    : 'text-slate-50 group-hover:text-sky-400'
                  }
                `}
              >
                {title}
              </h3>

              {description && (
                <p className="mt-2 font-sans text-slate-400 line-clamp-2">
                  {description}
                </p>
              )}

              {dueDate && (
                <div className="mt-3 flex items-center gap-2 text-sm text-slate-500">
                  <ClockIcon className="h-4 w-4" />
                  <time dateTime={dueDate}>
                    {new Date(dueDate).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric'
                    })}
                  </time>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Completed indicator bar */}
        {completed && (
          <motion.div
            initial={{ scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ duration: 0.3, ease: [0.65, 0, 0.35, 1] }}
            className="h-1 bg-gradient-to-r from-emerald-500 to-sky-500 origin-left"
          />
        )}
      </div>
    </motion.article>
  );
}
```

**Usage**:
```typescript
// app/tasks/page.tsx
import { TaskCard } from '@/components/ui/task-card';

export default function TasksPage() {
  const tasks = [
    {
      id: 1,
      title: 'Design new landing page',
      description: 'Create mockups for the updated homepage with dark theme',
      completed: false,
      dueDate: '2025-12-25'
    },
    // ... more tasks
  ];

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-24">
      <div className="mx-auto max-w-3xl">
        <header className="mb-16">
          <h1 className="font-serif text-6xl font-light tracking-tight text-slate-50">
            Your Tasks
          </h1>
          <p className="mt-4 font-sans text-lg text-slate-400">
            {tasks.length} items to complete
          </p>
        </header>

        <div className="space-y-3">
          {tasks.map((task, i) => (
            <TaskCard
              key={task.id}
              {...task}
              index={i}
              onToggle={(id) => console.log('Toggle task', id)}
            />
          ))}
        </div>
      </div>
    </main>
  );
}
```

This implementation demonstrates:
- ✅ Cinematic aesthetic (dark theme, gradients, shadows)
- ✅ Distinctive typography (Space Grotesk implied)
- ✅ Purposeful motion (stagger, hover, complete animation)
- ✅ Accessibility (ARIA labels, keyboard support, semantic HTML)
- ✅ Performance (Client Component only for interactivity)
- ✅ States (default, hover, completed)
- ✅ Polish (gradient overlay, color transitions, scale effects)

---

**Final Directive**: Use this skill to create interfaces that feel crafted, not generated. Make bold design choices. Trust your aesthetic instincts. Surprise with quality.

---
id: 001
title: Create comprehensive UI design skill
stage: general
date: 2025-12-21
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: Muhammad Maaz
command: general-request
labels: ["design-system", "ui", "skill", "documentation", "tailwind"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - SKILL.md
tests:
  - none
---

## Prompt

Create a comprehensive UI design skill for my Todo app that will be used across all pages (landing, sign-in, sign-up, and main app). Save it as a SKILL.md file.

The skill should define:

## Design Philosophy
- Modern, clean, and minimalist aesthetic
- Professional yet approachable feel
- Subtle depth through shadows and layering
- Micro-interactions that delight without distracting

## Color System
Create a cohesive color palette with:
- Primary color (for CTAs, active states, key actions)
- Secondary/accent color (for highlights, badges, secondary actions)
- Neutral scale (at least 8 shades from near-white to near-black)
- Semantic colors (success, warning, error, info)
- Background colors (main bg, card bg, elevated surfaces)
- Ensure AAA accessibility contrast ratios for text
- Include both light mode colors (and optionally dark mode)

## Typography
- Primary font family (suggest a modern Google Font pairing)
- Font size scale (xs through 4xl minimum)
- Line heights and letter spacing for each size
- Font weights to use and when

## Spacing & Layout
- Consistent spacing scale (4px base recommended)
- Container max-widths for different contexts
- Responsive breakpoints
- Grid system guidelines

## Components Specifications
Define styling for these core components:
- Buttons (primary, secondary, ghost, danger - with hover/focus/active/disabled states)
- Input fields (default, focus, error, disabled states)
- Cards (with subtle shadows and hover lift effects)
- Navigation bar (sticky, with blur backdrop)
- Links (with underline animations)
- Checkboxes/toggles (with smooth transitions)
- Badges and tags
- Modal/dialog styling
- Toast notifications

## Animation Guidelines
Include specific CSS/Tailwind animations for:
- Page transitions (fade-in on load)
- Button hover effects (scale, shadow lift, color transitions)
- Input focus animations (border glow, label float)
- Card hover (subtle lift with shadow expansion)
- Checkbox completion (satisfying checkmark animation)
- Loading states (skeleton screens, spinners)
- Micro-interactions (ripple effects, success confirmations)
- Staggered list animations (items appearing sequentially)
- Smooth scrolling behavior
- Transition timing functions (use easing curves, not linear)

Specify duration guidelines:
- Instant feedback: 100-150ms
- Simple transitions: 200-300ms
- Complex animations: 300-500ms
- Page transitions: 400-600ms

## Specific Page Guidelines

### Landing Page
- Hero section with animated gradient or subtle background motion
- Feature cards with hover animations
- Testimonial carousel (if applicable)
- CTA buttons that draw attention

### Auth Pages (Sign-in/Sign-up)
- Centered card layout
- Form field animations
- Password strength indicator animation
- Social login button styling
- Error shake animation for validation

### Main App (Todo Interface)
- Sidebar navigation (collapsible with animation)
- Todo item completion animation (strikethrough + fade)
- Add task animation (slide in from top/bottom)
- Delete animation (slide out + fade)
- Drag and drop visual feedback
- Empty state illustration styling
- Progress indicators

## Code Implementation Notes
- Use Tailwind CSS classes where possible
- Include custom CSS for complex animations
- Provide reusable component patterns
- Include CSS variables for easy theming
- Ensure all animations respect prefers-reduced-motion

## Example Code Snippets
Include ready-to-use code for:
- The custom Tailwind config extensions needed
- Key animation keyframes
- Reusable component class patterns
- A sample button component showing all states
- A sample input component with animations

Make this skill detailed enough that any page styled following it will look cohesive, professional, and polished. The animations should feel smooth and purposeful, never gimmicky.

## Response snapshot

Created a comprehensive 1000+ line UI Design System skill document (SKILL.md) for the Todo app with:

**Complete Design System:**
- Design philosophy with modern minimalism and accessibility-first principles
- Full color palette (primary, accent, neutral, semantic) with AAA contrast ratios
- Typography system using Inter font with 8-level size scale
- 4px-based spacing system with responsive breakpoints
- Dark mode support (optional)

**Component Specifications:**
- Buttons: 4 variants (primary, secondary, ghost, danger) with all states
- Input fields: default, focus, error, disabled with floating labels
- Cards: standard, hoverable, elevated variants
- Navigation: sticky with backdrop blur
- Checkboxes/toggles: custom designs with smooth animations
- Badges, modals, toasts with ready-to-use Tailwind classes

**Animation System:**
- 20+ custom Tailwind animations (fadeIn, slideUp, shake, shimmer, etc.)
- Complete keyframes definitions
- Duration scale (100ms-600ms)
- Easing functions (ease-out for responsiveness)
- GPU-accelerated properties only (transform, opacity)
- Full prefers-reduced-motion support

**Page-Specific Guidelines:**
- Landing page: hero section, feature cards, CTA sections with code examples
- Auth pages: centered card layout, floating labels, password strength indicator
- Main app: sidebar navigation, todo items with completion animations, empty states

**Code Implementation:**
- Complete Tailwind config extension (colors, animations, keyframes)
- Global CSS setup with font imports
- 3 reusable TypeScript/React components (Button, Input, Card)
- All components fully typed and accessible

**Developer Experience:**
- Ready-to-copy code snippets throughout
- Usage guidelines (DO/DON'T lists)
- Maintenance schedule and version history
- Consistent API across all components

The design system ensures every page built with it will have a cohesive, professional appearance with delightful micro-interactions that enhance UX without being distracting.

## Outcome

- ✅ Impact: Established foundation for consistent, professional UI across entire Todo app
- 🧪 Tests: No tests required (documentation/design system)
- 📁 Files: Created SKILL.md (1000+ lines)
- 🔁 Next prompts: Implement landing page using this design system, create auth pages with these styles, build main app interface
- 🧠 Reflection: Comprehensive design system provides clear guidelines for all UI development, ensuring consistency and professional polish across the application

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (documentation artifact)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Apply this design system to create the first page (landing or auth) to validate completeness and usability

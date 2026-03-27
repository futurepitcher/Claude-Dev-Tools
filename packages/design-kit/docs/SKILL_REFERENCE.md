# Skill Reference

Quick reference for all claude-design-kit skills. For detailed documentation, read the individual skill files in `skills/`.

## Workflow Recommendations

### New project
1. `/teach-impeccable` -- Set up design context
2. `/ui-ux-pro-max` -- Generate design system
3. `/frontend-design` -- Build components
4. `/polish` -- Final pass

### Improving existing UI
1. `/teach-impeccable` -- If no `.impeccable.md` exists
2. `/audit` -- Identify issues
3. `/critique` -- Get design director feedback
4. Fix issues with targeted skills:
   - Typography issues -> `/typeset`
   - Layout issues -> `/arrange`
   - Color issues -> `/colorize`
   - Copy issues -> `/clarify`
   - Motion issues -> `/animate`
5. `/polish` -- Final pass

### Making it bolder
`/bolder` -> `/animate` -> `/polish`

### Making it calmer
`/quieter` -> `/distill` -> `/polish`

### Production hardening
`/harden` -> `/optimize` -> `/adapt` -> `/polish`

### Design system extraction
`/audit` -> `/extract` -> `/normalize`

## Skill Quick Reference

### /teach-impeccable
**When**: Start of any new project. Run once.
**What**: Interactive questionnaire that creates `.impeccable.md` with your design context.
**Output**: `.impeccable.md` file in project root.

### /ui-ux-pro-max
**When**: Need a complete design system recommendation.
**What**: BM25 search engine across 67 styles, 96 palettes, 57 font pairings.
**Output**: Design system with pattern, style, colors, typography, effects.

### /frontend-design
**When**: Building new UI components or pages.
**What**: Principles for distinctive, production-grade interfaces. Anti-AI-slop guidelines.
**Output**: Working code with bold aesthetic direction.

### /bolder
**When**: Design feels too safe, generic, or boring.
**What**: Amplifies typography, color, spatial drama, motion, composition.
**Warning**: AI slop trap -- "bolder" does not mean more gradients and glassmorphism.

### /quieter
**When**: Design feels too aggressive, overwhelming, or overstimulating.
**What**: Reduces saturation, visual weight, decorative elements, motion intensity.

### /polish
**When**: Before shipping. Feature is functionally complete.
**What**: Pixel-perfect alignment, interaction states, transitions, copy consistency.

### /audit
**When**: Need comprehensive quality assessment.
**What**: Checks accessibility, performance, theming, responsive, anti-patterns.
**Output**: Severity-rated report with recommended fix skills.

### /critique
**When**: Need honest design feedback.
**What**: Design director-level assessment of hierarchy, emotion, composition.
**Output**: Anti-patterns verdict, priority issues, provocative questions.

### /animate
**When**: Interface feels static or lacks feedback.
**What**: Entrance choreography, micro-interactions, state transitions, easing curves.

### /typeset
**When**: Typography feels generic or inconsistent.
**What**: Font selection, type scale, hierarchy, readability, weight consistency.

### /colorize
**When**: Interface is too monochromatic or gray.
**What**: Semantic color, accent strategy, background tinting, OKLCH palettes.

### /arrange
**When**: Layout feels monotonous or has weak hierarchy.
**What**: Spacing systems, visual rhythm, grid variety, depth management.

### /clarify
**When**: Copy is unclear, jargon-heavy, or unhelpful.
**What**: Error messages, form labels, CTAs, empty states, confirmation dialogs.

### /delight
**When**: Interface is functional but joyless.
**What**: Micro-interactions, playful copy, illustrations, easter eggs, celebrations.

### /distill
**When**: Interface is too complex or cluttered.
**What**: Remove redundancy, progressive disclosure, simplify layout and content.

### /onboard
**When**: Users struggle to get started.
**What**: Welcome flows, empty states, contextual tooltips, guided tours.

### /adapt
**When**: Need to work across different devices or contexts.
**What**: Mobile, tablet, desktop, print, email adaptation strategies.

### /harden
**When**: Preparing for production reality.
**What**: Text overflow, i18n, error handling, edge cases, accessibility resilience.

### /normalize
**When**: Feature deviates from design system.
**What**: Replace one-offs with design system components and tokens.

### /extract
**When**: Patterns are duplicated across codebase.
**What**: Extract components, tokens, and patterns into design system.

### /optimize
**When**: Interface feels slow.
**What**: Loading, rendering, animation, image, and bundle optimization.

### /overdrive
**When**: Want to push past conventional limits.
**What**: View Transitions, WebGL, scroll-driven animations, spring physics, WASM.

### /remotion-best-practices
**When**: Building programmatic video with Remotion.
**What**: Composition, sequencing, audio, 3D, captions, text animation patterns.

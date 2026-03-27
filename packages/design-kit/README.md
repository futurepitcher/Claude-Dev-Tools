# Claude Design Kit

**AI-powered design intelligence for Claude Code.**

24 design skills. 67 styles. 96 color palettes. 57 font pairings. 25 chart types. 13 framework stacks. One toolkit.

Claude Design Kit gives Claude Code the design knowledge to build distinctive, production-grade interfaces -- not generic AI slop. It includes a searchable design database with BM25 ranking, anti-AI-aesthetic principles, and specialized skills for every stage of the design process.

---

## What's Inside

```
67 UI styles          Glassmorphism, brutalism, claymorphism, neumorphism,
                      bento grid, dark mode, minimalism, skeuomorphism, and 59 more

96 color palettes     Product-specific palettes for SaaS, e-commerce, fintech,
                      healthcare, beauty, gaming, education, and more

57 font pairings      Curated Google Fonts pairs with CSS imports, Tailwind config,
                      and mood/style classification

25 chart types        Data visualization recommendations by data type with
                      library suggestions and accessibility notes

13 tech stacks        React, Next.js, Vue, Nuxt, Svelte, SwiftUI, React Native,
                      Flutter, Tailwind, shadcn/ui, Jetpack Compose, Astro

99 UX guidelines      Prioritized rules with do/don't examples and code samples

24 design skills      From initial concept to final polish
```

---

## Quick Install

### Project-level

```bash
git clone https://github.com/christopherpitcher/claude-design-kit.git .claude-design-kit
cd .claude-design-kit && ./install.sh
```

### Global (all projects)

```bash
git clone https://github.com/christopherpitcher/claude-design-kit.git ~/claude-design-kit
cd ~/claude-design-kit && ./install.sh --global
```

### One-liner

```bash
git clone https://github.com/christopherpitcher/claude-design-kit.git ~/claude-design-kit && ~/claude-design-kit/install.sh --global
```

No dependencies beyond Python 3 (for the search engine) and Claude Code.

---

## Skills Catalog

### Set Up

| Skill | What it does |
|-------|-------------|
| `/teach-impeccable` | One-time project setup. Gathers your brand, audience, and aesthetic direction into a persistent context file. |
| `/ui-ux-pro-max` | Generate a complete design system. Searches 5 domains in parallel, applies reasoning rules, returns colors, typography, style, and anti-patterns. |
| `/frontend-design` | Core design principles. Anti-AI-slop guidelines, bold aesthetics, context gathering protocol. Foundation for all other skills. |

### Adjust

| Skill | What it does |
|-------|-------------|
| `/bolder` | Turn up the volume. Amplify typography, color, spatial drama. Make safe designs memorable. |
| `/quieter` | Turn it down. Reduce saturation, weight, decoration. Refined sophistication. |
| `/colorize` | Add strategic color to monochromatic interfaces. Semantic color, OKLCH palettes, accent strategy. |
| `/typeset` | Fix typography. Font selection, modular scales, hierarchy, readability, weight consistency. |
| `/animate` | Add purposeful motion. Entrance choreography, micro-interactions, timing, easing. |
| `/arrange` | Fix layout and spacing. Visual rhythm, grid variety, z-index management, depth. |
| `/overdrive` | Push past limits. Shaders, View Transitions, spring physics, scroll-driven animation, WebGL. |

### Ship

| Skill | What it does |
|-------|-------------|
| `/polish` | Final quality pass. Pixel-perfect alignment, interaction states, transitions, copy. |
| `/audit` | Comprehensive quality report. Accessibility, performance, theming, responsive. Severity-rated. |
| `/critique` | Design director feedback. AI slop detection, hierarchy assessment, priority issues. |

### Improve

| Skill | What it does |
|-------|-------------|
| `/clarify` | Better copy. Error messages, form labels, CTAs, empty states. Plain language, helpful, human. |
| `/delight` | Add joy. Micro-interactions, playful copy, celebrations, easter eggs. |
| `/distill` | Remove complexity. Progressive disclosure, ruthless simplification. |
| `/onboard` | Better first impressions. Welcome flows, empty states, contextual tooltips. |
| `/adapt` | Cross-device. Mobile, tablet, desktop, print, email adaptation strategies. |
| `/harden` | Production ready. Error handling, i18n, overflow, edge cases, RTL support. |

### System

| Skill | What it does |
|-------|-------------|
| `/normalize` | Align with your design system. Replace one-offs with tokens and components. |
| `/extract` | Extract reusable patterns into your design system. |
| `/optimize` | Performance. Loading, rendering, animation, images, Core Web Vitals. |
| `/remotion-best-practices` | Video creation in React with Remotion. |

---

## Usage Examples

### Generate a design system

```
> /ui-ux-pro-max

Generate a design system for a fintech SaaS dashboard targeting CFOs
```

Or use the search engine directly:

```bash
python3 skills/ui-ux-pro-max/scripts/search.py "fintech saas dashboard professional" --design-system -p "FinTrack"
```

### Build with context

```
> /teach-impeccable     # Run once to set up project context
> /frontend-design      # Then build with full design intelligence

Build a settings page with sidebar navigation, account section, and billing section
```

### Refine iteratively

```
> /critique             # Get honest feedback on what you built
> /typeset              # Fix the typography issues it found
> /colorize             # Add warmth to the monochromatic palette
> /polish               # Final pass before shipping
```

### Before/after with /bolder

**Before**: A safe, generic dashboard with system fonts, gray cards, and no personality.

**After**: Distinctive typography with dramatic scale jumps, bold color accents, asymmetric layout with intentional white space, and purposeful motion on page load.

### Before/after with /distill

**Before**: A cluttered settings page with 30+ visible options, nested cards, and competing CTAs.

**After**: Clean single-column flow with progressive disclosure. Primary actions obvious. Secondary options tucked behind expandable sections.

---

## The Anti-Slop Philosophy

Claude Design Kit is built on one core belief: **AI-generated interfaces should be indistinguishable from human-designed ones.**

Every skill includes anti-pattern detection for the telltale signs of AI-generated design:

- Cyan-on-dark color palettes with purple-to-blue gradients
- Glassmorphism blur effects used as decoration
- Gradient text on metrics and headings
- Dark mode with neon accents as a default
- Identical card grids (icon + heading + text, repeated)
- Hero metric layouts (big number, small label, gradient)
- Inter, Roboto, or system fonts with no personality
- Rounded rectangles with generic drop shadows
- Bounce/elastic easing curves
- Sparklines as decoration

The `/critique` and `/audit` skills explicitly check for these patterns and call them out.

---

## Stack Support

Skills provide framework-specific guidance for:

| Stack | Key Focus |
|-------|-----------|
| **HTML + Tailwind** | Utilities, responsive, accessibility |
| **React** | State, hooks, performance, patterns |
| **Next.js** | SSR, routing, images, API routes |
| **Vue** | Composition API, Pinia, Vue Router |
| **Nuxt.js** | Server components, auto-imports |
| **Svelte** | Runes, stores, SvelteKit |
| **SwiftUI** | Views, State, Navigation, Animation |
| **React Native** | Components, Navigation, Lists |
| **Flutter** | Widgets, State, Layout, Theming |
| **shadcn/ui** | Components, theming, forms, CVA |
| **Jetpack Compose** | Composables, Modifiers, State |
| **Astro** | Islands, content, static generation |

---

## Architecture

```
claude-design-kit/
  skills/
    SKILLS_INDEX.md                 # Full catalog
    ui-ux-pro-max/                  # Design system generator
      SKILL.md                      #   Skill definition
      scripts/                      #   BM25 search engine (Python)
        search.py                   #     CLI entry point
        core.py                     #     BM25 implementation
        design_system.py            #     Design system generation
      data/                         #   CSV databases
        styles.csv                  #     67 UI styles
        colors.csv                  #     96 color palettes
        typography.csv              #     57 font pairings
        charts.csv                  #     25 chart types
        products.csv                #     Product type recommendations
        landing.csv                 #     Landing page patterns
        ux-guidelines.csv           #     99 UX rules
        ui-reasoning.csv            #     Style-to-product reasoning
        icons.csv                   #     Icon recommendations
        react-performance.csv       #     React performance rules
        web-interface.csv           #     Web interface guidelines
        stacks/                     #     13 framework-specific CSVs
    frontend-design.md              # Core design principles
    frontend-design-reference/      # Detailed reference guides
      typography.md                 #   Type scales, pairing, loading
      color-and-contrast.md         #   OKLCH, palettes, dark mode
      spatial-design.md             #   Grids, rhythm, container queries
      motion-design.md              #   Timing, easing, reduced motion
      interaction-design.md         #   Forms, focus, loading
      responsive-design.md          #   Mobile-first, fluid design
      ux-writing.md                 #   Labels, errors, empty states
    [20 individual skill files]     # One .md per skill
  agents/
    accessibility-auditor.md        # WCAG 2.1 AA compliance
    ui-migration-architect.md       # Cross-framework migration
  rules/
    frontend-architecture.md        # Architecture patterns
  docs/
    GETTING_STARTED.md              # Installation and first steps
    DESIGN_SYSTEM_GUIDE.md          # Using the design system generator
    SKILL_REFERENCE.md              # Quick reference for all skills
  install.sh                        # Installer (--global or --project)
  uninstall.sh                      # Uninstaller
```

---

## How It Works

1. **`/teach-impeccable`** gathers your project's design context (audience, brand, aesthetic direction) and saves it to `.impeccable.md`. This file persists across Claude Code sessions.

2. **Every design skill** checks for this context before proceeding. If it doesn't exist, the skill will prompt you to run `/teach-impeccable` first. This prevents generic output.

3. **The UI/UX Pro Max search engine** uses BM25 text ranking across CSV databases to find the most relevant styles, colors, typography, and patterns for your specific product type and keywords.

4. **Skills compose** -- you can chain `/bolder` -> `/animate` -> `/polish` for a complete refinement pass, or use `/audit` to identify issues and then apply targeted fixes with individual skills.

---

## Contributing

Contributions welcome. The highest-impact areas:

- **New styles** in `skills/ui-ux-pro-max/data/styles.csv`
- **New color palettes** in `skills/ui-ux-pro-max/data/colors.csv`
- **New font pairings** in `skills/ui-ux-pro-max/data/typography.csv`
- **Stack-specific guidelines** in `skills/ui-ux-pro-max/data/stacks/`
- **New skills** for specialized design domains
- **Reference guides** in `skills/frontend-design-reference/`

---

## License

MIT -- see [LICENSE](LICENSE).

---

Built for designers and frontend developers who believe AI should raise the bar, not lower it.

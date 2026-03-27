# Design System Guide

## Using the Design System Generator

The UI/UX Pro Max skill includes a BM25 search engine with 67 styles, 96 color palettes, 57 font pairings, and comprehensive UI reasoning rules.

### Generate a Complete Design System

```bash
python3 skills/ui-ux-pro-max/scripts/search.py "healthcare saas dashboard" --design-system -p "MedTrack"
```

This searches 5 domains in parallel (product, style, color, landing, typography), applies reasoning rules, and returns a complete recommendation including:

- **Pattern**: Landing page structure and section order
- **Style**: Visual style with effects, complexity, and framework compatibility
- **Colors**: Primary, secondary, CTA, background, and text colors
- **Typography**: Font pairings with Google Fonts URLs and Tailwind config
- **Effects**: Animation, shadows, and visual treatment recommendations
- **Anti-patterns**: What to avoid for this product type

### Persist for Hierarchical Retrieval

```bash
# Create master design system file
python3 skills/ui-ux-pro-max/scripts/search.py "healthcare saas" --design-system --persist -p "MedTrack"

# Create page-specific override
python3 skills/ui-ux-pro-max/scripts/search.py "healthcare dashboard analytics" --design-system --persist -p "MedTrack" --page "dashboard"
```

This creates:
- `design-system/medtrack/MASTER.md` -- Global source of truth
- `design-system/medtrack/pages/dashboard.md` -- Dashboard-specific overrides

When building a page, check `pages/[page].md` first. If it exists, its rules override MASTER.md.

### Domain-Specific Searches

```bash
# Style exploration
python3 skills/ui-ux-pro-max/scripts/search.py "glassmorphism dark elegant" --domain style

# Typography options
python3 skills/ui-ux-pro-max/scripts/search.py "luxury serif modern" --domain typography

# Color palettes
python3 skills/ui-ux-pro-max/scripts/search.py "fintech trust professional" --domain color

# Chart recommendations
python3 skills/ui-ux-pro-max/scripts/search.py "real-time metrics dashboard" --domain chart

# UX best practices
python3 skills/ui-ux-pro-max/scripts/search.py "animation accessibility loading" --domain ux

# Landing page structure
python3 skills/ui-ux-pro-max/scripts/search.py "hero testimonial pricing" --domain landing
```

### Stack-Specific Guidelines

```bash
# Get React-specific best practices
python3 skills/ui-ux-pro-max/scripts/search.py "performance bundle optimization" --stack react

# Tailwind patterns
python3 skills/ui-ux-pro-max/scripts/search.py "responsive layout accessibility" --stack html-tailwind

# SwiftUI guidelines
python3 skills/ui-ux-pro-max/scripts/search.py "navigation state animation" --stack swiftui
```

Available stacks: `html-tailwind`, `react`, `nextjs`, `vue`, `svelte`, `swiftui`, `react-native`, `flutter`, `shadcn`, `jetpack-compose`, `astro`, `nuxtjs`, `nuxt-ui`

## Data Files

The search engine uses CSV databases in `skills/ui-ux-pro-max/data/`:

| File | Records | Content |
|------|---------|---------|
| `styles.csv` | 67 styles | Style categories, effects, best-for, prompts, CSS keywords |
| `colors.csv` | 96 palettes | Product-specific color palettes with hex values |
| `typography.csv` | 57 pairings | Font pairings with Google Fonts URLs and Tailwind config |
| `charts.csv` | 25 types | Chart type recommendations by data type |
| `products.csv` | Product types | Style recommendations by product category |
| `landing.csv` | Landing patterns | Page structure and CTA strategies |
| `ux-guidelines.csv` | 99 rules | UX best practices with do/don't examples |
| `ui-reasoning.csv` | Reasoning rules | Logic for style-to-product matching |
| `icons.csv` | Icon library | Icon recommendations by category |
| `react-performance.csv` | React rules | Performance guidelines for React |
| `web-interface.csv` | Web rules | General web interface guidelines |

## The `.impeccable.md` File

When you run `/teach-impeccable`, it creates a `.impeccable.md` file in your project root with your design context:

```markdown
## Design Context

### Users
[Who they are, their context, the job to be done]

### Brand Personality
[Voice, tone, 3-word personality, emotional goals]

### Aesthetic Direction
[Visual tone, references, anti-references, theme]

### Design Principles
[3-5 principles guiding all design decisions]
```

All design skills check for this file before proceeding. Without it, skills will prompt you to run `/teach-impeccable` first. This ensures every design decision is grounded in your specific project context rather than generic AI defaults.

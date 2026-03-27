# Getting Started with Claude Design Kit

## Prerequisites

- [Claude Code](https://claude.com/claude-code) installed and configured
- Python 3.8+ (for the design system search engine)
- A project you want to improve

## Installation

### Project-level (recommended)

```bash
cd your-project
git clone https://github.com/your-username/claude-design-kit.git .claude-design-kit
cd .claude-design-kit && ./install.sh
```

This installs skills into your project's `.claude/skills/` directory. Skills are available when working in this project.

### Global installation

```bash
git clone https://github.com/your-username/claude-design-kit.git ~/claude-design-kit
cd ~/claude-design-kit && ./install.sh --global
```

This installs skills into `~/.claude/skills/`, making them available in every project.

## First Steps

### 1. Set up design context

Run `/teach-impeccable` in Claude Code. This interactive skill will:
- Scan your project's existing code and design patterns
- Ask you targeted questions about your brand, audience, and aesthetic direction
- Save a `.impeccable.md` file to your project root

This file becomes the persistent design context that all other skills reference. You only need to run this once per project.

### 2. Generate a design system

Use the UI/UX Pro Max skill to generate design recommendations:

```
/ui-ux-pro-max
```

Or run the search engine directly:

```bash
python3 .claude/skills/ui-ux-pro-max/data/../scripts/search.py "fintech saas dashboard" --design-system -p "My App"
```

### 3. Build something

Ask Claude Code to build a component or page. The design skills will automatically inform its choices:

```
Build a settings page with a sidebar navigation and form sections
```

### 4. Refine iteratively

Use the adjustment skills to dial in the result:

- `/polish` -- Final quality pass for pixel-perfect details
- `/bolder` -- If the design feels too safe
- `/quieter` -- If the design feels too aggressive
- `/typeset` -- If typography needs work
- `/colorize` -- If it needs more visual warmth

## Skill Categories

### Start here
- `/teach-impeccable` -- One-time project setup
- `/frontend-design` -- Build distinctive interfaces
- `/ui-ux-pro-max` -- Generate complete design systems

### Adjust the volume
- `/bolder` -- Turn it up
- `/quieter` -- Bring it down
- `/colorize` -- Add strategic color
- `/typeset` -- Fix typography
- `/animate` -- Add purposeful motion
- `/arrange` -- Fix layout and spacing

### Ship with confidence
- `/polish` -- Final quality pass
- `/audit` -- Comprehensive quality report
- `/critique` -- Design director feedback
- `/harden` -- Production resilience

### Improve UX
- `/clarify` -- Better copy and messaging
- `/delight` -- Add joy and personality
- `/distill` -- Remove unnecessary complexity
- `/onboard` -- Improve first-time experience
- `/adapt` -- Cross-device adaptation

### System building
- `/normalize` -- Align with design system
- `/extract` -- Extract reusable patterns
- `/optimize` -- Performance improvement

## Tips

1. **Always run `/teach-impeccable` first** -- without design context, skills produce generic output
2. **Combine skills** -- `/bolder` then `/polish` is a powerful sequence
3. **Use `/audit` before shipping** -- it catches issues other skills miss
4. **The search engine is powerful** -- try different keywords to explore the full style database
5. **Skills reference each other** -- `/frontend-design` is the foundation that other skills build on

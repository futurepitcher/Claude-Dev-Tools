# Claude Dev Tools

> Battle-tested Claude Code configuration for building world-class applications.

Three packages. Zero dependencies. Install in 30 seconds. Immediately elevate every Claude Code session with specialist agents, design intelligence, and prompt optimization.

---

## What's Inside

### [Toolkit](packages/toolkit/) -- Core Engineering

35 specialist agents that auto-trigger on file changes, 5 composable skills, 4 workflow pipelines, 3 quality hooks, and 4 context-aware rules.

| Component | Count | Highlights |
|-----------|-------|------------|
| **Agents** | 35 | Security hardener, type enforcer, perf tuner, concurrency auditor, impact analyst, dependency auditor, and 29 more |
| **Skills** | 5 | `/plan` (architecture-first planning), `/tdd` (RED-GREEN-REFACTOR), `/deslop` (remove AI cruft), `/session` (context save/restore), `/learner` (auto-extract insights) |
| **Workflows** | 4 | Bug fix, feature development, incident response, research |
| **Hooks** | 3 | Pre-tool (phase gates, credential blocking, dangerous command detection), post-tool (secret scanning, regression alerts), memory-check |
| **Rules** | 4 | TypeScript (strict typing, no `any`), Python (no bare except, type hints), testing (TDD, AAA pattern), database migrations (naming, rollback) |

Agents are organized into 8 categories: code quality, security, performance, architecture, reliability, testing, investigation, and research. They auto-trigger based on which files you change -- edit a route file and the security hardener and API contract generator activate automatically.

### [Design Kit](packages/design-kit/) -- UI/UX Intelligence

24 design skills backed by a searchable database of 67 UI styles, 96 color palettes, 57 font pairings, 25 chart types, and 13 framework stacks.

| Phase | Skills | Purpose |
|-------|--------|---------|
| **Set Up** | `/teach-impeccable`, `/ui-ux-pro-max`, `/frontend-design` | Establish design context, generate design systems, set anti-AI-slop principles |
| **Adjust** | `/bolder`, `/quieter`, `/colorize`, `/typeset`, `/animate`, `/arrange`, `/overdrive` | Amplify, reduce, add color, fix typography, add motion, fix layout, push limits |
| **Ship** | `/polish`, `/audit`, `/critique` | Final quality pass, comprehensive audit, design director feedback |
| **Improve** | `/clarify`, `/delight`, `/distill`, `/onboard`, `/adapt`, `/harden` | Better copy, add joy, simplify, improve onboarding, cross-device, production-ready |
| **System** | `/normalize`, `/extract`, `/optimize`, `/remotion-best-practices` | Design system alignment, pattern extraction, performance, video |

Built on one core belief: AI-generated interfaces should be indistinguishable from human-designed ones. Every skill includes anti-pattern detection for the telltale signs of AI-generated design.

### [Prompt Engine](packages/prompt-engine/) -- Meta-Intelligence

7 skills that transform how you interact with Claude Code. From fast prompt enhancement to fully autonomous execution pipelines.

| Skill | What It Does | When to Use |
|-------|-------------|-------------|
| `/meta` | Full prompt operating system -- classifies tasks, gathers context, scores and refines prompts | Complex, multi-faceted requests |
| `/meta-lite` | Fast prompt enhancer -- sharper clarity in seconds | Quick upgrades to rough prompts |
| `/meta-engineering` | Backend-focused optimizer with engineering doctrine | API, database, migration, integration work |
| `/meta-design` | Frontend-focused optimizer with UX quality bar | Component, design system, visual QA work |
| `/deep-interview` | Socratic requirements gathering with ambiguity scoring | Unclear scope, before autonomous execution |
| `/autopilot` | 5-phase zero-intervention pipeline (expand, plan, execute, QA, validate) | Well-scoped features, hands-off execution |
| `/ultrawork` | Maximum parallelism with smart model routing | Bulk operations across many files |

---

## Quick Install

### Everything, globally

```bash
git clone https://github.com/futurepitcher/Claude-Dev-Tools.git ~/Claude-Dev-Tools
cd ~/Claude-Dev-Tools && ./install.sh --all --global
```

### One-liner

```bash
git clone https://github.com/futurepitcher/Claude-Dev-Tools.git ~/Claude-Dev-Tools && ~/Claude-Dev-Tools/install.sh --all --global
```

### Specific packages

```bash
./install.sh --toolkit --global          # Just the engineering toolkit
./install.sh --design-kit --global       # Just the design kit
./install.sh --prompt-engine --global    # Just the prompt engine
./install.sh --toolkit --prompt-engine --global  # Mix and match
```

### Project-level (current project only)

```bash
./install.sh --all --project
```

### Interactive

```bash
./install.sh    # Prompts for target and package selection
```

### Uninstall

```bash
./uninstall.sh --global              # Remove everything
./uninstall.sh --global --toolkit    # Remove just the toolkit
```

---

## Architecture

Each package is fully standalone. No hard dependencies between them.

```
Claude-Dev-Tools/
  install.sh                  # Master installer (handles all packages)
  uninstall.sh                # Master uninstaller
  packages/
    toolkit/                  # Core engineering (agents, skills, workflows, hooks, rules)
    design-kit/               # UI/UX intelligence (skills, agents, palettes, typography)
    prompt-engine/            # Meta-intelligence (prompt optimization, autonomous execution)
```

### How Installation Works

The installer creates **symlinks** from your `.claude/` directory to the package source files. This means:

- Updates are instant -- `git pull` and you have the latest version
- No files are copied into your project
- Safe to re-run (idempotent)
- Easy to uninstall (just remove symlinks)

### Package Independence

```
toolkit          design-kit       prompt-engine
   |                |                  |
   v                v                  v
~/.claude/       ~/.claude/         ~/.claude/
  agents/          skills/            skills/
  skills/          (design skills)    (meta skills)
  workflows/
  hooks/
  rules/
```

You can install any combination. The toolkit provides the broadest coverage (agents, hooks, rules). Design kit and prompt engine are skill-focused and layer cleanly on top.

---

## Usage Examples

### Engineering workflow

```
> /plan                    # Architecture-first planning
> /tdd                     # RED-GREEN-REFACTOR cycle
> /deslop                  # Clean up AI-generated cruft
> /session save            # Save context for later
```

### Design workflow

```
> /teach-impeccable        # Set up design context (run once)
> /frontend-design         # Build with design intelligence
> /critique                # Get honest feedback
> /polish                  # Final quality pass
```

### Prompt optimization workflow

```
> /meta Add real-time collaboration to the editor
  # Returns: classified, grounded, scored, enhanced prompt

> /meta-lite Fix the login page
  # Returns: quick upgrade in seconds

> /deep-interview A smart notification system
  # Returns: structured spec after Socratic Q&A

> /autopilot Add user preferences to the settings page
  # Runs: expand -> plan -> execute -> QA -> validate (autonomous)
```

---

## Agent Trigger Matrix

When you install the toolkit, agents auto-activate based on file changes:

| File Pattern | Agents Triggered |
|--------------|------------------|
| `*.ts`, `*.tsx` | type-enforcer, security-hardener |
| `*.py` | security-hardener, documentation-validator |
| `*.sql`, `migrations/*` | db-migration-validator, data-integrity-validator |
| `package.json` | dependency-auditor, bundle-optimizer |
| `.env*`, `*config*` | configuration-validator |
| `src/api/routes/*` | api-contract-generator, security-hardener, impact-analyst |
| `src/services/*` | impact-analyst, modularity-enforcer |

---

## Contributing

### Adding an agent

1. Create a markdown file in `packages/toolkit/agents/{category}/`
2. Include frontmatter with name, description, and model tier
3. Add to `packages/toolkit/agents/AGENT_INDEX.md`

### Adding a design skill

1. Create a markdown file in `packages/design-kit/skills/`
2. Include frontmatter with name and description
3. Add to `packages/design-kit/skills/SKILLS_INDEX.md`

### Adding a prompt engine skill

1. Create a markdown file in `packages/prompt-engine/skills/`
2. Include frontmatter with name, description, and args
3. Update `packages/prompt-engine/README.md`

### General guidelines

- Follow existing file formats (look at similar files for structure)
- Keep skills self-contained (no external dependencies)
- Test with `claude code` before submitting
- Strip project-specific references (keep skills generic)

---

## Packages

| Package | Description | Docs |
|---------|-------------|------|
| [Toolkit](packages/toolkit/) | 35 agents, 5 skills, 4 workflows, 3 hooks, 4 rules | [README](packages/toolkit/README.md) |
| [Design Kit](packages/design-kit/) | 24 design skills, 67 styles, 96 palettes | [README](packages/design-kit/README.md) |
| [Prompt Engine](packages/prompt-engine/) | 7 meta-intelligence skills | [README](packages/prompt-engine/README.md), [Guide](packages/prompt-engine/docs/PROMPT_ENGINEERING.md) |

---

## License

MIT -- see [LICENSE](LICENSE).

---

Built with patterns extracted from thousands of hours of production AI-assisted development. Every agent, skill, and workflow has been battle-tested on real-world applications.

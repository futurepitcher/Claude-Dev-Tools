# Prompt Engine

**Meta-intelligence layer for Claude Code.** Turn rough ideas into world-class execution prompts with task classification, codebase grounding, quality scoring, and smart routing.

7 skills that make every Claude Code session dramatically more effective.

---

## Skills

| Skill | Purpose | Speed | Depth |
|-------|---------|-------|-------|
| `/meta` | Full prompt operating system | Moderate | Maximum |
| `/meta-lite` | Fast prompt enhancer | Fast | Light |
| `/meta-engineering` | Backend/systems optimizer | Moderate | Deep |
| `/meta-design` | Frontend/UX optimizer | Moderate | Deep |
| `/deep-interview` | Socratic requirements gathering | Slow (interactive) | Maximum |
| `/autopilot` | Zero-intervention execution pipeline | Fast (autonomous) | Full |
| `/ultrawork` | Maximum parallelism engine | Fast (parallel) | Full |

---

## When to Use What

```
Is your request clear and well-scoped?
  |
  +-- YES: Is it a single task or many independent tasks?
  |         |
  |         +-- Single task --> /autopilot
  |         +-- Many tasks --> /ultrawork
  |
  +-- NO: Do you need full architecture analysis?
  |        |
  |        +-- YES: Is it frontend or backend?
  |        |         |
  |        |         +-- Frontend --> /meta-design
  |        |         +-- Backend  --> /meta-engineering
  |        |         +-- Both     --> /meta
  |        |
  |        +-- NO: Just need a quick upgrade?
  |                 |
  |                 +-- YES --> /meta-lite
  |                 +-- NO: Requirements are unclear?
  |                          |
  |                          +-- YES --> /deep-interview
```

---

## Skill Details

### /meta -- Prompt Operating System

The full-power prompt optimizer. Classifies tasks into 15 categories, detects complexity, gathers codebase context, composes an enhanced prompt with role assignment, constraint injection, chain-of-thought scaffolding, and validation criteria. Scores the result on 10 dimensions and refines before presenting.

**Best for**: Complex, multi-faceted requests where you want maximum prompt quality.

```
/meta Add a real-time collaboration feature to the document editor
```

**Output**: Task classification, complexity rating, execution shape recommendation, fully enhanced prompt with architecture grounding, constraints, and success criteria, quality score, and an offer to execute.

### /meta-lite -- Fast Prompt Enhancer

A lightweight optimizer that upgrades rough prompts in seconds. No architecture audit, no scoring rubric -- just sharp improvements to role clarity, objective precision, constraints, and output format.

**Best for**: Quick upgrades when you know what you want but want it stated better.

```
/meta-lite Fix the login page
```

**Output**: Prompt title, execution target, upgraded prompt, one-line note on what was improved.

### /meta-engineering -- Backend-Focused Optimizer

Specialized for backend, API, database, migration, integration, and infrastructure work. Adds engineering-specific doctrine: audit-first, reuse over rebuild, canonical contracts, staged implementation, regression protection.

**Best for**: API endpoints, database migrations, service integrations, performance optimization, debugging.

```
/meta-engineering Migrate the auth system from sessions to JWTs
```

**Output**: Task classification, complexity, execution shape, scored prompt with architecture grounding, execution recommendation with suggested skills/agents.

### /meta-design -- Frontend-Focused Optimizer

Specialized for UI, UX, design systems, theming, visual QA, and frontend performance. Ensures prompts address state correctness, loading/error/empty states, responsive behavior, and premium quality bar.

**Best for**: Component development, design system work, visual QA, frontend performance, product polish.

```
/meta-design Build a settings page with sidebar navigation and dark mode support
```

**Output**: Prompt title, execution target, execution shape, scored prompt with UX grounding, optional alternate versions (more design-forward, more QA-ruthless, etc.).

### /deep-interview -- Socratic Requirements Gathering

An interactive interview process that mathematically scores ambiguity across 4 dimensions (Goal, Constraints, Success Criteria, Context). Asks 2-3 questions per round for up to 8 rounds. Includes adversarial challenge rounds at rounds 4 and 6. Produces a structured specification when ambiguity drops below 20%.

**Best for**: Complex features with unclear scope, requests that could be interpreted multiple ways, before autonomous execution.

```
/deep-interview A smart notification system that learns which notifications I care about
```

**Output**: Structured spec with goal, requirements (with acceptance criteria), constraints, edge cases, out-of-scope items, and verification plan.

### /autopilot -- Zero-Intervention Pipeline

A 5-phase autonomous pipeline: Expansion (analyze codebase) -> Planning (break into tasks) -> Execution (run with model routing) -> QA Cycling (build/test/lint loops) -> Validation (requirement mapping). Circuit breaker halts after 3 failures. 15-minute timeout.

**Best for**: Well-understood features where you want hands-off execution.

```
/autopilot Add a daily focus score widget to the dashboard
```

### /ultrawork -- Maximum Parallelism Engine

Decomposes requests into atomic tasks, routes each to the optimal model tier (Haiku/Sonnet/Opus), and fires all independent tasks simultaneously. Enforces strict parallelism rules: same file = sequential, type dependency = sequential, everything else = parallel.

**Best for**: Bulk operations across multiple files, adding tests to many services, renaming across a codebase.

```
/ultrawork Write unit tests for all 6 service files in src/services/
```

---

## Composing Skills

Skills chain naturally:

```
/deep-interview --> spec --> /autopilot       # Clarify then execute
/meta --> enhanced prompt --> execute          # Optimize then run
/meta-engineering --> /ultrawork              # Optimize then parallelize
```

---

## Installation

Prompt Engine is part of [Claude Dev Tools](../../README.md). Install with:

```bash
./install.sh --prompt-engine --global
```

Or install everything:

```bash
./install.sh --all --global
```

---

## License

MIT -- see [LICENSE](../../LICENSE).

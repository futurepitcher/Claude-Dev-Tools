---
name: learner
description: Auto-extract non-obvious, project-specific insights from debugging sessions and implementation work
invoke: /learner [--review]
category: meta
---

# /learner — Skill Extraction Engine

Automatically extracts **non-obvious, project-specific insights** from your development work and saves them as reusable knowledge. Captures the kind of knowledge that:

1. Is NOT easily searchable online
2. IS specific to this codebase
3. Required genuine investigation or debugging to discover

## When to Use

- After fixing a tricky bug
- After discovering a non-obvious codebase pattern
- After a debugging session that taught you something
- Periodically (weekly) to review accumulated learnings
- Run with `--review` to see and curate saved skills

## Extraction Process

### 1. Scan Recent Work
Review the current session's activities:
- Files read and modified
- Errors encountered and resolved
- Patterns discovered during exploration
- Workarounds applied

### 2. Triple Confirmation Gate

Each potential skill must pass 3 checks:

| Check | Question | Fail = Skip |
|-------|----------|-------------|
| **Searchability** | Could someone find this in official docs or Stack Overflow? | Yes = skip |
| **Specificity** | Is this specific to this codebase (not general programming)? | No = skip |
| **Discovery Cost** | Did it require genuine debugging/investigation to learn? | No = skip |

### 3. Skill Format

```markdown
---
type: feedback
---

[Rule or insight]

**Why:** [How this was discovered]

**How to apply:** [When and where this knowledge is relevant]
```

### 4. Storage

Skills are saved to the Claude Code memory system for future retrieval.

## Examples of Good Skills

**Good** (passes triple gate):
- "SQLite `INSERT OR REPLACE` on parent tables with `ON DELETE CASCADE` FKs silently deletes all child rows. Use UPDATE for existing, INSERT for new."
- "The config parser silently ignores unknown keys — if you add a new config option, you must also add it to the validation schema or it will be dropped."
- "Test fixtures in `tests/fixtures/` are shared across suites — modifying them can break unrelated tests."

**Bad** (fails triple gate):
- "Use `async/await` instead of `.then()` chains" — searchable, general
- "React components should be functional" — obvious, general
- "Always handle errors" — generic advice

## Usage

```
/learner                    # Extract skills from current session
/learner --review           # Review and curate saved skills
/learner --since yesterday  # Extract from recent git history
```

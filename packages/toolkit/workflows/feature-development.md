# Workflow: Feature Development

> End-to-end feature implementation with research, TDD, and team review.

## Pipeline

```
PHASE: research
  - Use research agents (codebase-locator, codebase-analyzer, pattern-finder)
  - Understand existing patterns before writing code

PHASE: plan
  - Brainstorm 3+ approaches
  - Architecture planning skill
  - User approval required before implementation

LOOP: tdd-cycle (repeat per unit of work)
  |
  +- RED: Write failing test
  |
  +- GREEN: Implement minimum code to pass
  |
  +- REFACTOR: Clean up while tests pass
  |
  +- GATE: all tests pass

GATE: build
  - Build succeeds
  - Zero errors

TEAM: review-team (parallel)
  - Architecture Reviewer
  - Code Quality Reviewer
  - Security Reviewer
  - Synthesize findings

CHECKPOINT: commit
  - Pre-commit quality gate
  - Conventional commit message
  - Push to remote
```

## When to Use

- New features requiring 3+ files
- Features touching multiple layers (API + service + repository)
- Any work that needs planning before implementation

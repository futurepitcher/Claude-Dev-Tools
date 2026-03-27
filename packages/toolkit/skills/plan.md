# Skill: Architecture Planning

> Research-first planning with brainstorming, constraint checking, and approval gates.

## When to Use

- New feature requiring multiple files or services
- Significant refactoring or migration
- Any task touching 3+ files or 2+ layers

## Workflow

### 1. Research

Before proposing any architecture, use the research agents:
- `codebase-locator` — find all related files
- `codebase-analyzer` — understand existing patterns
- `pattern-finder` — find similar implementations
- `docs-locator` — find relevant documentation

### 2. Brainstorm

Generate at least 3 distinct approaches:
- **Approach A**: [description + tradeoffs]
- **Approach B**: [description + tradeoffs]
- **Approach C**: [description + tradeoffs]

Score each on: solves problem, simplicity, reversibility, pattern consistency.

### 3. Plan

Write a structured plan with:
- Files to create/modify (with line estimates)
- Dependencies and ordering
- Test strategy
- Rollback plan

### 4. Validate

Before implementing, verify:
- [ ] No constraint violations (check CLAUDE.md critical constraints)
- [ ] Follows existing patterns (from research phase)
- [ ] Test strategy defined
- [ ] Smallest possible scope

### 5. Await Approval

Mark plan as **"AWAITING APPROVAL"** and wait for explicit approval before writing any code.

## Critical Rule

```
NO CODE UNTIL PLAN APPROVED

In planning mode:
  DO analyze and explore (read-only)
  DO generate detailed plans
  DO ask clarifying questions
  DO document architectural decisions

  DO NOT write code to source files
  DO NOT run modification commands
  DO NOT make changes without approval
```

## Integration

- Invoked by: `/plan`, `/create_plan`
- Uses agents: codebase-locator, codebase-analyzer, pattern-finder, docs-locator

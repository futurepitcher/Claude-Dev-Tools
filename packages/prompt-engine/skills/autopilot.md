---
name: autopilot
description: Autonomous 5-phase execution pipeline -- from idea to verified code without intervention
invoke: /autopilot <description>
category: execution
---

# /autopilot -- Autonomous Execution Pipeline

Run a fully autonomous 5-phase pipeline that takes a feature description from idea to verified, committed code. Autopilot is a **zero-intervention pipeline** that expands scope, plans, executes, QA-cycles, and validates -- all without stopping.

## When to Use

- You have a well-understood feature and want hands-off execution
- The scope is moderate (1-5 files, not a major refactor)
- You trust the pipeline to make reasonable decisions

## Pipeline

### Phase 1: Expansion (Read-Only)
Analyze the request and expand into concrete requirements:
1. Search the codebase for related code, patterns, and conventions
2. Identify affected files, dependencies, and test coverage
3. Produce a structured brief: **what** to build, **where** it goes, **how** it connects

### Phase 2: Planning (Read-Only)
Create an actionable implementation plan:
1. Break the expanded brief into 3-6 discrete tasks
2. Identify task dependencies (what blocks what)
3. Estimate complexity per task (simple/moderate/complex)
4. Select appropriate agent for each task (Haiku for simple, Sonnet for moderate, Opus for complex)
5. Define verification criteria for each task

### Phase 3: Execution (Read/Write)
Execute each task in dependency order:
1. For each task, launch the appropriate agent
2. Independent tasks run in parallel via worktrees when possible
3. Each task produces: files changed, tests added, build status
4. **Circuit breaker**: If a task fails 3 times, halt and report

### Phase 4: QA Cycling (up to 5 iterations)
Verify the implementation meets requirements:
1. Run build -- fix any compilation errors
2. Run tests -- fix any test failures
3. Run type-check on changed files
4. Verify no lint errors in changed files
5. If issues found, diagnose and fix (up to 5 cycles)
6. **Halt condition**: 3 consecutive identical errors = stop and report

### Phase 5: Validation (Read-Only)
Final verification before presenting results:
1. Map each original requirement to VERIFIED / PARTIAL / MISSING
2. Run a diff review for code quality
3. Summarize: files created, files modified, tests added, coverage delta
4. Present results to user for approval

## Usage

```
/autopilot Add a daily focus score widget to the dashboard that calculates
a weighted score from completed tasks, habit data, and meeting-free time
```

## Flags

- `--dry-run` -- Run Phase 1-2 only, show plan without executing
- `--skip-qa` -- Skip Phase 4 QA cycling (use when you'll QA manually)
- `--verbose` -- Show all agent output in real-time

## Differences from Other Modes

| Mode | Trigger | Stops When | Human Input |
|------|---------|------------|-------------|
| `/autopilot` | Feature description | All phases pass or circuit breaker | None until end |
| `/ship` | Plan file | Review passes | Approve/reject at review |
| `/ultrawork` | Bulk operations | All tasks complete | None until end |

## Error Handling

- **Phase failure**: Log which phase failed, what was attempted, and why
- **Circuit breaker**: After 3 failures on same task, halt with diagnostic
- **Timeout**: 15 minutes total. If exceeded, save state and report progress
- **Rollback**: All work happens on a branch. If validation fails completely, branch is preserved but not merged

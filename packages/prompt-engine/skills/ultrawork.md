---
name: ultrawork
description: Maximum parallelism engine -- fire all independent tasks simultaneously with smart model routing
invoke: /ultrawork <description>
category: execution
---

# /ultrawork -- Maximum Parallelism Engine

Execute tasks with **maximum parallelism**. Every independent operation fires simultaneously. Smart model routing assigns Haiku for trivial tasks, Sonnet for implementation, Opus for architecture decisions. Background execution for anything over 30 seconds.

## When to Use

- Multiple independent changes across different files/modules
- Bulk operations (rename across codebase, add tests to 10 files, update 5 API endpoints)
- Time-sensitive work where serial execution is too slow
- Tasks where order doesn't matter

## How It Works

### 1. Decompose
Break the request into atomic tasks. Identify dependencies:
- **Independent tasks**: Can run simultaneously (different files, no shared state)
- **Dependent tasks**: Must wait for predecessors (e.g., types before implementation)
- **Fan-out/Fan-in**: Many parallel tasks that merge into one result

### 2. Route Models
Assign each task to the optimal model tier:

| Complexity | Model | Examples |
|------------|-------|----------|
| Trivial | Haiku | Rename variable, add import, fix typo |
| Standard | Sonnet | Implement function, write test, add endpoint |
| Complex | Opus | Architecture decision, complex refactor, security audit |

### 3. Fire All
Launch all independent tasks simultaneously using the Agent tool:
- Each task gets its own agent with focused instructions
- Use `run_in_background: true` for operations > 30 seconds
- Use `isolation: "worktree"` when tasks modify overlapping files

### 4. Merge Results
Collect results as agents complete:
- Verify no conflicts between parallel changes
- Run build + tests once all tasks complete
- Report: tasks completed, files changed, any conflicts

## Usage

```
/ultrawork Add error handling to all 8 API route files in src/api/routes/
```

```
/ultrawork Write unit tests for: UserService, AuthService,
NotificationService, and PaymentProcessor
```

## Flags

- `--serial` -- Force sequential execution (debug mode)
- `--dry-run` -- Show task decomposition without executing
- `--model <tier>` -- Force all tasks to use one model tier

## Parallelism Rules

1. **Same file = sequential**. Never have two agents edit the same file
2. **Type dependency = sequential**. If task B imports types from task A, B waits
3. **Everything else = parallel**. Maximize concurrent execution
4. **Merge conflicts = halt**. If parallel edits conflict, stop and report

## Example Decomposition

Request: "Add input validation to all API endpoints"

```
Task 1 (Haiku):  Create Zod schemas in src/validation/schemas.ts
Task 2 (Sonnet): Add validation to POST /api/users           [depends: 1]
Task 3 (Sonnet): Add validation to POST /api/orders          [depends: 1]
Task 4 (Sonnet): Add validation to POST /api/payments        [depends: 1]
Task 5 (Sonnet): Add validation to POST /api/notifications   [depends: 1]
Task 6 (Sonnet): Write tests for all validations             [depends: 2,3,4,5]

Execution: Task 1 -> [Tasks 2,3,4,5 in parallel] -> Task 6
```

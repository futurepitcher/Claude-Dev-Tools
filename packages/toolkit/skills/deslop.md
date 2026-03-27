---
name: deslop
description: Regression-safe code cleanup — remove AI-generated cruft with deletion-first approach
invoke: /deslop [path]
category: quality
---

# /deslop — AI Slop Cleaner

Regression-safe code cleanup that removes **AI-generated cruft** — over-engineered abstractions, unnecessary comments, dead code, redundant error handling, and "just in case" configurability. Uses a **deletion-first approach**: remove before refactoring.

## When to Use

- After a large AI-generated implementation
- When code feels bloated or over-engineered
- Before a PR review to clean up AI artifacts
- When you notice patterns like: excessive comments, unnecessary try/catch, wrapper functions that add no value

## AI Slop Patterns (What to Remove)

### Comments & Documentation
- Obvious comments: `// increment counter` above `counter++`
- Section dividers that add no information: `// ========`
- Redundant JSDoc that restates the function signature
- "AI disclaimer" comments

### Over-Engineering
- Wrapper functions that just forward to another function
- Abstractions with exactly one implementation
- Configuration objects for things that never change
- Factory patterns for creating a single type
- "Strategy" patterns with one strategy

### Defensive Coding
- Try/catch around code that can't throw
- Null checks on values that are always defined
- Default parameters that are never used differently
- Validation of internal (non-boundary) data

### Dead Code
- Unused imports, variables, and functions
- Commented-out code blocks
- Unreachable branches
- Feature flags that are always on/off

### Verbose Patterns
- `if (condition) { return true; } else { return false; }` -> `return condition;`
- Unnecessary intermediate variables
- Explicit `undefined` returns
- Redundant type assertions

## Process

### Phase 1: Protect (Read-Only)
1. Run existing tests to establish a green baseline
2. If tests fail, stop — don't clean up code with broken tests
3. Identify test coverage gaps in target files

### Phase 2: Classify
1. Read target files (or all recently modified files)
2. Classify each issue by slop category
3. Rate severity: **cosmetic** (comment cruft) vs **structural** (over-engineering)

### Phase 3: Execute (Smell-Focused Passes)
Run one pass per smell category, in order of safety:
1. **Dead code removal** — safest, no behavior change possible
2. **Comment cleanup** — cosmetic, no behavior change
3. **Simplification** — reduce verbose patterns
4. **Abstraction removal** — inline unnecessary wrappers
5. **Defensive code removal** — remove impossible-path checks

After EACH pass:
- Run tests
- If any test fails, revert the pass and skip that category

### Phase 4: Verify
1. Run full test suite
2. Diff line count: report lines removed
3. Run build to verify compilation

## Usage

```
/deslop src/services/
/deslop   # Clean all files modified since last commit
```

## Safety Guarantees

- Tests must pass before and after every pass
- Each category is an independent pass — failure in one doesn't block others
- No behavioral changes — only structural cleanup
- If in doubt, leave it in — false positives are worse than false negatives

# Elite Claude Code Development Practices

> **The Elite Developer's Mantra:** Plan deliberately. Implement incrementally. Verify thoroughly. Remember intelligently.

---

## Three Pillars of Elite Development

```
    DELIBERATE       STRATEGIC        ROBUST
    PLANNING         MEMORY           QUALITY
                                      GATES

    Architecture     Context that     Verification
    before code      persists         at every step
```

---

## Session Management

### Session Startup Checklist

```bash
# 1. Start fresh (if new task)
/clear

# 2. Verify context loaded
# Claude reads CLAUDE.md automatically

# 3. Understand current state
git status
git log --oneline -5

# 4. Review relevant context
# Read files related to your task
```

### Model Selection Guide

| Task Type | Model | Rationale |
|-----------|-------|-----------|
| Complex planning, architecture | **Opus** | Deep reasoning, comprehensive analysis |
| Feature implementation | **Sonnet** | Balance of cost and quality |
| Simple refactoring, formatting | **Haiku** | Fast, cost-effective |
| Bug investigation | **Sonnet** | Good debugging capability |
| Code review | **Sonnet** | Comprehensive coverage |

### Clear Between Tasks

Run `/clear` before starting unrelated work to prevent context pollution and reduce token consumption.

---

## The Elite Developer Rhythm

```
1. SESSION START
   /clear if new task
   Verify CLAUDE.md loaded
   Understand context

2. PLANNING PHASE
   /plan to generate architecture
   Review and critique plan
   Approve before implementation

3. IMPLEMENTATION PHASE
   Small, incremental steps
   Tests first (TDD)
   Run quality gates after each step
   Commit atomic changes

4. VERIFICATION PHASE
   All tests pass
   Code review (human)
   Security scan
   Update memory if patterns discovered

5. COMPLETION
   /commit with clear message
   Update relevant docs
   /clear before next task
```

---

## The 5-Phase Planning Protocol

### Phase 1: Load Context
- Read CLAUDE.md and project structure
- Analyze relevant source files
- Understand existing patterns, map dependencies

### Phase 2: Analyze
- Break feature into sequential tasks
- Identify data structures needed
- List edge cases and risks

### Phase 3: Constraint Check
- Verify against architectural rules
- Check naming conventions
- Validate security implications

### Phase 4: Plan Output
- Implementation roadmap, file-by-file changes
- Testing strategy, rollback considerations
- Mark: **"AWAITING APPROVAL"**

### Phase 5: Human Review
- Critique for blind spots
- Simplify where possible
- Approve or iterate

```
CRITICAL RULE: NO CODE UNTIL PLAN APPROVED
```

---

## TDD Cycle with AI

```
RED      Write failing test first
         Define expected behavior with edge cases

GREEN    Minimal code to pass test
         Feed test results back, iterate until passing

REFACTOR Clean up while tests pass
         Tests provide safety net

         REPEAT
```

---

## Three-Tier Code Review

```
TIER 1: AI First-Pass
  Syntax errors, obvious bugs, style violations, security patterns

TIER 2: Automated Testing
  Unit tests, integration tests, coverage, performance benchmarks

TIER 3: Human Review
  Architecture decisions, business logic, security implications
  Final authority
```

---

## Quality Gate Checklist

Before every commit:

- [ ] Lint passes (0 errors)
- [ ] Type check passes (0 errors)
- [ ] All tests pass
- [ ] Coverage not decreased
- [ ] No console.log/debugger
- [ ] No hardcoded secrets
- [ ] Human review completed

---

## Memory Maintenance

### Bootstrap
Run `/init` on new projects to auto-generate initial CLAUDE.md

### Checkpoint
Before major refactoring: "Update memory files with current decisions"

### Quarterly Review
- Remove outdated instructions
- Update evolved patterns
- Add discovered conventions

---

## Simplicity Imperative

> "The best code is the code you don't write."

### Build Iteratively
Generate piece by piece, testing after each part. Never generate entire features at once.

### Avoid Over-Engineering
- Don't add features beyond what was asked
- Don't refactor surrounding code unnecessarily
- Don't add "just in case" configurability

### The Rule of Three
Three similar lines of code > premature abstraction. Only abstract after three instances of duplication.

---

*Elite practices derived from Anthropic documentation and battle-tested community patterns.*

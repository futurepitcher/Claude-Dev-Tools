# Prompt Engineering Guide

A practical guide to writing world-class prompts for Claude Code, distilled from the techniques powering the `/meta` family of prompt optimizers.

---

## Prompt Architecture Principles

### 1. Specificity Beats Length

A 3-line prompt with precise constraints outperforms a 30-line prompt with vague guidance. Every sentence should increase the probability of the correct output.

**Weak**: "Make the API better and add some tests."

**Strong**: "Add pagination to GET /api/users (limit/offset query params, default limit 20, max 100). Return `{ data: User[], total: number, hasMore: boolean }`. Add integration tests for: default pagination, custom limit, limit exceeding max, empty results."

### 2. Role + Mission + Constraints

The three pillars of an effective prompt:

- **Role**: Who should Claude be? Not "a developer" but "a senior TypeScript architect specializing in REST API design with deep knowledge of Express middleware patterns."
- **Mission**: What specific outcome is required? Measurable, bounded, unambiguous.
- **Constraints**: What must NOT happen? Explicit negative constraints prevent the most common failures.

### 3. Context Over Instruction

Claude Code has access to the codebase. Instead of describing what exists, point to it:

**Weak**: "The database uses SQLite and we have a repository pattern with base classes."

**Strong**: "Follow the repository pattern in `src/repositories/UserRepository.ts`. Use the same SQLite connection from `src/database/connection.ts`."

### 4. Validation Closes the Loop

Every prompt should define what "done" looks like:

- Build commands that must pass
- Test commands that must pass
- Behavioral checks (curl, UI verification)
- Regression safeguards

Without validation criteria, you are relying on hope.

---

## Task Classification Framework

Every request falls into one or more categories. Identifying the category shapes the optimal prompt structure.

### The 15 Categories

| Category | Key Signals | Prompt Bias |
|----------|-------------|-------------|
| **Implementation** | "add", "create", "build" | Audit-first, layer isolation, tests |
| **Debugging** | "fix", "error", "broken", stack traces | Reproduce, isolate, root cause, minimal fix |
| **Planning** | "plan", "design", "architect" | Research, constraints, alternatives, trade-offs |
| **Refactoring** | "refactor", "clean up", "simplify" | Preserve behavior, TDD, incremental |
| **Analysis** | "explain", "why", "trace" | Read-only, evidence-based, structured output |
| **Migration** | "migrate", "rename", "upgrade" | Current/target state, shims, staged cutover |
| **Integration** | "connect", "sync", "webhook" | Adapter pattern, error handling, retry logic |
| **QA / Audit** | "test", "qa", "verify" | Inventory, severity triage, regression |
| **Performance** | "slow", "optimize", "latency" | Measure first, critical path, before/after |
| **Design / UI** | "component", "page", "style" | State correctness, responsive, premium quality |
| **Product Strategy** | "roadmap", "prioritize", "ship" | Must-ship vs defer, user impact, compound value |
| **Executive** | "pitch", "narrative", "deck" | Audience, thesis, structure, tone |
| **Security** | "audit", "vulnerability", "PII" | OWASP, compliance, defense in depth |
| **Documentation** | "document", "README", "ADR" | Audience, accuracy, maintenance burden |
| **DevOps** | "deploy", "CI", "Docker" | Idempotent, rollback, monitoring |

### Complexity Levels

| Level | Description | Prompt Strategy |
|-------|-------------|-----------------|
| **Simple** | Single file, clear fix | Direct prompt, minimal context |
| **Compound** | Multiple files, one layer | Sequenced steps, file list |
| **Programmatic** | Cross-layer, contract-dependent | Phased execution, gates |
| **Foundational** | Architecture-level, system-wide | Audit-first, migration plan |

---

## Execution Shapes

The structure of a prompt matters as much as its content. Choose the right shape:

### Single
One prompt, execute directly. For simple, bounded tasks.

### Audit-First
Read and understand before changing. For architecture-sensitive changes or unfamiliar codebases.

```
Phase 1 (read-only): Audit the current implementation of X
Phase 2 (read/write): Implement the changes based on audit findings
```

### Phased
Sequential stages with gates between them. For multi-stage work with dependencies.

```
Phase 1: Create types and interfaces
Phase 2: Implement repository layer [depends on Phase 1]
Phase 3: Implement service layer [depends on Phase 2]
Phase 4: Add API routes [depends on Phase 3]
Phase 5: Write tests [depends on Phase 4]
```

### Parallel
Independent tracks that can run concurrently. For clean splits after contract freeze.

```
Track A (backend): API endpoints
Track B (frontend): UI components
Track C (tests): Integration tests
Merge: Integration verification
```

### Debug
Structured investigation pipeline.

```
1. Reproduce the issue
2. Isolate the failing component
3. Identify root cause
4. Implement smallest correct fix
5. Verify fix and add regression test
```

### Migration
Current state to target state with backward compatibility.

```
1. Document current state
2. Define target state and terminology mapping
3. Create compatibility shims
4. Migrate in stages with validation at each stage
5. Remove shims after cutover period
```

---

## Quality Scoring Rubric

Use this rubric to evaluate prompt quality before execution:

| Dimension | Weight | Score 1 | Score 3 | Score 5 |
|-----------|--------|---------|---------|---------|
| **Intent Preservation** | High | User's goal is lost | Partially captured | Perfectly preserved and sharpened |
| **Clarity** | High | Ambiguous, multiple interpretations | Mostly clear, some gaps | Unambiguous, one interpretation |
| **Architecture Awareness** | High | Ignores codebase reality | References some patterns | Deeply grounded in existing code |
| **Execution Readiness** | High | Requires significant interpretation | Mostly executable | Copy-paste executable |
| **Validation Rigor** | Medium | No success criteria | Build/test mentioned | Specific commands, expected outcomes |
| **Ambiguity Reduction** | Medium | Same ambiguity as input | Some clarification | All ambiguity resolved |
| **Product Quality** | Medium | No quality bar | Mentions quality | Defines premium UX expectations |
| **Codebase Relevance** | Medium | Generic advice | Some file references | Specific files, patterns, conventions |
| **Parallelization** | Low | Not considered | Mentioned | Clean independent tracks defined |
| **Elegance** | Low | Cluttered, redundant | Readable | Minimal, every word earns its place |

**Scoring rule**: If any high-weight dimension scores below 4, refine the prompt before using it.

---

## Prompt Anti-Patterns

### The Kitchen Sink
Adding every possible instruction "just in case." Result: Claude gets confused by contradictory or irrelevant guidance.

**Fix**: Include only constraints relevant to this specific task.

### The Vague Mandate
"Make it better." "Clean up the code." "Improve performance."

**Fix**: Define what "better" means. Specific metrics, specific files, specific outcomes.

### The Missing Negative
Telling Claude what to do but not what to avoid. Result: Claude makes reasonable but unwanted decisions.

**Fix**: Add explicit "DO NOT" constraints for common failure modes.

### The Context Dump
Pasting entire files or long descriptions when a file path reference would suffice.

**Fix**: Point to files. "Follow the pattern in `src/services/UserService.ts`."

### The Unvalidated Optimist
No success criteria, no verification steps. Trusting that the output is correct.

**Fix**: Always define how to verify the result. Build commands, test commands, manual checks.

---

## When to Use Which Tool

| Situation | Recommended Approach |
|-----------|---------------------|
| Quick fix, clear scope | Direct prompt (no meta needed) |
| Moderate task, want better prompt | `/meta-lite` |
| Complex backend task | `/meta-engineering` |
| Complex frontend task | `/meta-design` |
| Complex cross-cutting task | `/meta` |
| Unclear requirements | `/deep-interview` first |
| Well-scoped, want autonomous execution | `/autopilot` |
| Bulk operations across many files | `/ultrawork` |
| Already an expert, know exactly what you want | Direct prompt |

The best prompt engineers know when NOT to use a meta-prompt. If you can state the request clearly in 3 lines, just state it.

---

## Further Reading

- `/meta` skill definition: `skills/meta.md`
- `/meta-engineering` skill definition: `skills/meta-engineering.md`
- `/meta-design` skill definition: `skills/meta-design.md`
- `/deep-interview` skill definition: `skills/deep-interview.md`

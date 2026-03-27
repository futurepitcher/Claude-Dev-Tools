---
name: deep-interview
description: Socratic requirements gathering with mathematical ambiguity scoring before execution
invoke: /deep-interview <topic>
category: planning
---

# /deep-interview -- Ambiguity-Scored Requirements Gathering

A structured Socratic interview process that **mathematically scores ambiguity** across key dimensions before allowing execution to proceed. Ensures requirements are crystal clear before any code is written.

## When to Use

- Complex features with unclear scope
- User requests that could be interpreted multiple ways
- Before `/autopilot` or `/ultrawork` on non-trivial features
- When past builds were rejected due to misunderstood requirements

## Process

### Round Structure (up to 8 rounds)

Each round asks 2-3 targeted questions. After each round, compute an **ambiguity score** (0-100%) across 4 weighted dimensions:

| Dimension | Weight | Measures |
|-----------|--------|----------|
| **Goal** | 30% | What exactly should be built? |
| **Constraints** | 25% | Technical limits, patterns, must-not-do |
| **Success Criteria** | 25% | How do we know it's done correctly? |
| **Context** | 20% | Where does it fit, who uses it, edge cases |

### Scoring Formula

```
ambiguity = sum(dimension_weight * dimension_uncertainty)
```

Each dimension starts at 100% uncertain and decreases as questions are answered.

### Gate: Ambiguity <= 20%

- **> 60%**: Ask broad, exploratory questions
- **30-60%**: Ask focused, clarifying questions
- **20-30%**: Ask edge-case and confirmation questions
- **<= 20%**: Gate passes -- ready to execute

### Challenge Rounds (Rounds 4 and 6)

At rounds 4 and 6, shift to **adversarial mode**:
- "What if the user does X instead?"
- "What happens when Y fails?"
- "Is there a simpler way to achieve the same goal?"
- "What did you assume that might be wrong?"

### Output: Specification Document

When ambiguity <= 20%, produce a structured spec:

```markdown
## Feature: [Title]

### Goal
[1-2 sentence objective]

### Requirements
1. [Requirement with acceptance criterion]
2. [Requirement with acceptance criterion]
...

### Constraints
- [Technical constraint]
- [Design constraint]

### Edge Cases
- [Edge case and expected behavior]

### Out of Scope
- [Explicitly excluded items]

### Verification Plan
- [How to verify each requirement]
```

## Usage

```
/deep-interview A smart notification system that learns which notifications I care about
```

The interview produces a spec that can be piped directly into `/autopilot` or `/ship`:

```
/deep-interview -> spec -> /autopilot
```

## Flags

- `--fast` -- Cap at 4 rounds, gate at 30% ambiguity (less thorough)
- `--skip-challenges` -- Skip adversarial rounds 4 and 6
- `--output <path>` -- Save spec to file instead of inline

## Tips

- Give detailed initial descriptions to reduce rounds needed
- Answer with specifics, not "whatever works"
- The challenge rounds often surface the most valuable insights
- If you already have a spec, use `/autopilot` directly instead

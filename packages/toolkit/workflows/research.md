# Workflow: Research

> Deep codebase exploration with parallel research agents.

## Pipeline

```
PARALLEL: research-suite
  - codebase-locator: Find all related files by pattern
  - codebase-analyzer: Understand architecture and data flow
  - pattern-finder: Find similar implementations
  - docs-locator: Find relevant documentation
  - docs-analyzer: Extract key information from docs

PHASE: synthesize
  - Merge findings from all agents
  - Deduplicate and resolve conflicts
  - Identify gaps in understanding

CHECKPOINT: report
  - Structured research report
  - Key files identified
  - Patterns documented
  - Open questions flagged
```

## Output Format

```markdown
# Research Report: [topic]

## Key Files
[list with paths and purposes]

## Architecture
[how the system currently works]

## Patterns Found
[existing patterns to follow]

## Documentation
[relevant docs with links]

## Gaps
[things not yet understood]

## Recommendation
[how to proceed based on research]
```

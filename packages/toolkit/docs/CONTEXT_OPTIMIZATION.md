# Context Optimization Guide

> Effective context management is the difference between productive Claude Code sessions and frustrating, expensive ones.

---

## Why Context Matters

Claude Code is stateless but context-aware. Each message consumes tokens, and context pollution leads to:
- **Higher costs** (more tokens = more money)
- **Slower responses** (larger context takes longer to process)
- **Lower quality** (irrelevant context confuses the model)
- **Compaction artifacts** (auto-summarization loses detail)

---

## Token Management Strategies

### 1. Clear Between Tasks

**The most important practice.** Run `/clear` before starting unrelated work.

### 2. Use the Right Model

| Context Size | Recommended Model |
|--------------|-------------------|
| Small (simple tasks) | Haiku |
| Medium (features) | Sonnet |
| Large (architecture) | Opus |

Haiku costs ~10% of Opus. Use it for simple tasks.

### 3. Disable Unused MCP Servers

Each enabled MCP server adds tool definitions to context. Disable servers you're not actively using.

### 4. Prefer Focused Reads

Read specific line ranges when you know where to look, rather than entire files.

### 5. Use Grep Before Reading

Search first, then read only the relevant results. Avoid speculative reads of multiple files.

---

## Session Patterns

### Short Sessions (1-2 tasks)
```
/clear -> Task 1 -> /commit -> /clear -> Task 2 -> /commit
```

### Medium Sessions (Feature)
```
/clear -> /plan -> Approve -> Phase 1 -> /commit -> Phase 2 -> /commit -> /quality-gate -> Final commit
```

### Long Sessions (Architecture)
```
/clear -> Research (read-only) -> /plan -> Create handoff -> Break into multiple sessions
```

---

## Context Hygiene Checklist

### Before Starting
- [ ] `/clear` if starting new work
- [ ] Disable unnecessary MCP servers
- [ ] `git status` to understand current state

### During Work
- [ ] Read only files you need
- [ ] Use Grep before speculative reads
- [ ] Commit incrementally to establish checkpoints

### After Completing
- [ ] Commit final changes
- [ ] Create handoff if work continues later
- [ ] `/clear` before next task

---

## Signs of Context Problems

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| Claude forgets recent work | Context compacted | `/clear`, use handoffs |
| Responses getting slower | Large context | `/clear`, smaller sessions |
| Irrelevant suggestions | Context polluted | `/clear`, fresh start |
| Inconsistent code style | Mixed context | `/clear`, read style guide |

---

## Cost Optimization

| Task Type | Estimated Cost |
|-----------|----------------|
| Simple bug fix | $0.01-0.05 |
| Medium feature | $0.10-0.50 |
| Complex architecture | $1.00-5.00 |

### Reduce Costs
1. Use Haiku for simple tasks (10x cheaper than Opus)
2. Clear frequently (prevents context bloat)
3. Plan before coding (reduces wasted iterations)
4. Write good tests first (reduces debugging cycles)
5. Use handoffs (don't rebuild context repeatedly)

---

*Effective context management is a skill. Like muscle memory, it becomes automatic with practice.*

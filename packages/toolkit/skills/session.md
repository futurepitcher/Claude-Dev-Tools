# Skill: Session Management

> Save/restore context, create handoff documents, and track session metrics.

## Session Lifecycle

### Start Session
```
/session start
```
- Verify CLAUDE.md loaded
- Check git state
- Load any saved context
- Initialize metrics tracking

### During Session
- Hooks track tool usage in `.claude/memory/metrics.jsonl`
- Errors captured in `.claude/memory/errors.jsonl`
- Modified files tracked in `.claude/hooks/session_modified.txt`

### Pause Session (same person, later)
```
/session save
```
- Saves branch, task, files, state to `.claude/context/session-[timestamp].md`
- Resume with `/session restore`

### Transfer Session (different person or agent)
```
/session handoff
```
- Creates comprehensive handoff document including:
  - Current branch and uncommitted changes
  - Task description and progress
  - Key decisions made
  - Open questions
  - Next steps
- Resume with `/session resume`

### End Session
- `memory-check.sh` hook fires on Stop
- Checks if CLAUDE.md needs review
- Session metrics available via `/standup-notes`

## Continuous Learning

After each session:
- Error patterns captured to `errors.jsonl`
- Architecture decisions recorded to `decisions.jsonl`
- Code patterns tracked in `patterns.jsonl`
- Session metrics logged to `metrics.jsonl`

## Integration

- Hooks: memory-check.sh, post-tool.sh (metrics)
- Files: `.claude/memory/`, `.claude/context/`

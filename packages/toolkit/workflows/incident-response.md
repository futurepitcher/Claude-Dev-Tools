# Workflow: Incident Response

> Production incident triage, fix, and postmortem pipeline.

## Pipeline

```
PHASE: triage
  - Check service health endpoints
  - Classify severity: P0/P1/P2/P3

PHASE: investigate
  - Systematic debugging
  - Correlate with recent deploys (git log --since="2 hours ago")
  - Identify scope of impact

TEAM: debug-team
  - Debugger: trace root cause
  - System Architect: assess blast radius
  - Test Engineer: design verification test

PHASE: mitigate
  - Priority order:
    1. Rollback (git revert HEAD)
    2. Feature flag disable
    3. Service restart
    4. Workaround

PHASE: fix
  - Bug-fix workflow (test-first)
  - Verify fix resolves the incident

GATE: deploy
  - Build and test pass
  - Verify fix resolves the incident
  - Deploy with monitoring

CHECKPOINT: postmortem
  - Timeline documentation
  - Root cause analysis
  - Prevention action items
  - Save to memory for future reference
```

## Severity Classification

| Level | Criteria | Response Time |
|-------|----------|---------------|
| P0 | Service down, data loss | Immediate |
| P1 | Major feature broken | < 1 hour |
| P2 | Feature degraded, workaround exists | < 4 hours |
| P3 | Minor issue, cosmetic | Next sprint |

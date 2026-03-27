# Workflow: Bug Fix

> Systematic bug investigation and fix with test-first approach.

## Pipeline

```
PHASE: reproduce
  - Collect error details (logs, stack traces, reproduction steps)
  - Form 2+ hypotheses about root cause
  - Identify minimal reproduction case

TEAM: debug-team (if complex)
  - Debugger: trace execution, find root cause
  - System Architect: assess systemic impact
  - Test Engineer: design reproduction test

GATE: reproduction-test
  - Write test that fails reproducing the bug
  - Test MUST fail before fix

PHASE: fix
  - Implement smallest possible fix
  - Run reproduction test -> passes
  - Run full test suite -> all pass

GATE: verify
  - Build succeeds (zero errors)
  - All tests pass (100% pass rate)
  - Reproduction test specifically passes

CHECKPOINT: commit
  - Pre-commit quality gate
  - Commit message: "fix: [description]"
```

## When to Use

- Reported bugs
- Test failures
- Production errors (pair with incident-response workflow if urgent)

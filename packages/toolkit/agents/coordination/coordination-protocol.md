# Agent Coordination Protocol

Shared instructions for all agents operating in parallel teams.

## Before Starting Work

1. Your orchestrator has registered file claims for your scope
2. If you encounter a claim conflict warning during writes, **STOP** writing to that file
3. Report the conflict in your output so the orchestrator can resolve it
4. Only modify files within your declared scope

## During Execution

- Stay within your declared file scope
- If you discover issues in files outside your scope, **note them in your output** but do NOT edit them
- Record key discoveries that other agents should know about
- If another agent's work affects your analysis, note the dependency

## Output Format

Include a `## Coordination` section at the end of your output:

```markdown
## Coordination

### Files Modified
- `path/to/file.ts` — description of change

### Discoveries for Other Agents
- [Key finding that other agents should be aware of]

### Conflicts Encountered
- [Any claim conflicts or contradictions]

### Out-of-Scope Issues Found
- `path/to/other/file.ts` — [issue description, for orchestrator to route]
```

## Conflict Resolution Priority

When agents produce contradictory recommendations:

1. **Security** findings override all others
2. **Architecture** constraints override quality preferences
3. **Type safety** overrides convenience
4. **Test coverage** requirements are non-negotiable

If a genuine conflict exists (e.g., security vs performance), escalate to the orchestrator with both positions clearly stated.

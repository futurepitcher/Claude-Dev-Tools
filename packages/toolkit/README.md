# Claude Code Toolkit

**Production-grade Claude Code configuration for elite development teams.**

35 specialist agents, 5 skills, 4 workflows, 3 hooks, 4 rules, and battle-tested templates -- extracted from a real-world production codebase and generalized for any project.

---

## Why This Exists

Claude Code is powerful out of the box, but configuring it for professional workflows takes real effort. This toolkit gives you:

- **35 specialist agents** that auto-trigger on file changes (security audits on route changes, type enforcement on TypeScript, performance analysis on hot paths)
- **Workflow pipelines** for bug fixes, feature development, incident response, and research
- **Pre/post tool hooks** that catch secrets, block dangerous commands, detect `any` type regressions, and track session metrics
- **TDD enforcement** with phase gates (RED/GREEN/REFACTOR)
- **Session management** with context save/restore and handoff documents
- **Elite practices documentation** distilled from thousands of hours of AI-assisted development

Everything is MIT licensed and designed to be installed in minutes.

---

## Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/christopherpitcher/claude-code-toolkit/main/install.sh | bash
```

Or clone and install manually:

```bash
git clone https://github.com/christopherpitcher/claude-code-toolkit.git
cd claude-code-toolkit
./install.sh --project   # Install into current project's .claude/
# or
./install.sh --global    # Install into ~/.claude/ (applies to all projects)
```

## Uninstall

```bash
./uninstall.sh --project   # Remove from current project
# or
./uninstall.sh --global    # Remove from ~/.claude/
```

---

## What's Included

### Agents (35 specialists)

Agents are markdown instruction files that Claude Code loads to perform specialized analysis. They can be invoked manually or auto-triggered by file changes.

| Category | Agents | Purpose |
|----------|--------|---------|
| **Code Quality** (6) | type-enforcer, refactor-surgeon, modularity-enforcer, documentation-validator, accessibility-auditor, test-contract-author | Enforce strict typing, safe refactoring, DDD architecture, docs completeness, WCAG compliance, property-based tests |
| **Security** (4) | security-hardener, privacy-compliance-auditor, dependency-auditor, configuration-validator | OWASP Top 10, GDPR/CCPA, CVE scanning, secret detection |
| **Performance** (5) | perf-tuner, perf-monitor, database-query-optimizer, cost-optimizer, bundle-optimizer | Profile hot paths, track regressions, EXPLAIN plans, LLM token optimization, tree-shaking |
| **Architecture** (6) | api-contract-generator, api-versioning-strategist, db-migration-validator, data-integrity-validator, cross-platform-validator, component-extraction-planner | OpenAPI specs, deprecation paths, safe migrations, referential integrity, cross-stack compatibility, decomposition |
| **Reliability** (4) | error-resilience-validator, concurrency-auditor, observability-architect, deployment-strategist | Circuit breakers, race conditions, logging/tracing, blue-green/canary |
| **Testing** (2) | load-testing-designer, test-analyzer | k6/Artillery scenarios, root cause analysis |
| **Investigation** (6) | impact-analyst, codebase-locator, codebase-analyzer, pattern-finder, docs-locator, docs-analyzer | Blast radius scoring, file discovery, architecture understanding, pattern matching, doc search |
| **Research** (2) | technology-scout, tracer | Technology evaluation, evidence-driven causal analysis |

See [`agents/AGENT_INDEX.md`](agents/AGENT_INDEX.md) for the full catalog with trigger conditions.

### Skills (5)

Skills are composable capabilities invoked via slash commands.

| Skill | Command | Purpose |
|-------|---------|---------|
| **Architecture Planning** | `/plan` | Research-first planning with 3+ approaches, constraint checking, approval gates |
| **TDD Workflow** | `/tdd` | RED-GREEN-REFACTOR cycle with optional phase gate enforcement |
| **Deslop** | `/deslop` | Remove AI-generated cruft -- over-engineered abstractions, obvious comments, dead code |
| **Session Management** | `/session` | Save/restore context, create handoff documents, track metrics |
| **Learner** | `/learner` | Auto-extract non-obvious project-specific insights from debugging sessions |

### Workflows (4)

Declarative pipelines that orchestrate agents and skills for common scenarios.

| Workflow | Purpose |
|----------|---------|
| **Bug Fix** | Systematic investigation with reproduction test, minimal fix, full verification |
| **Feature Development** | Research, plan, TDD implementation, multi-agent review, commit |
| **Incident Response** | Triage, investigate, mitigate, fix, postmortem |
| **Research** | Parallel agent exploration with synthesis and gap analysis |

### Hooks (3)

Shell scripts that run before/after Claude Code tool invocations.

| Hook | Trigger | What It Does |
|------|---------|--------------|
| **pre-tool.sh** | Before Edit/Write/Bash | Phase gate enforcement, credential file blocking, dangerous command detection, `any` type baseline capture |
| **post-tool.sh** | After Edit/Write/Bash | Secret detection, console.log warnings, `any` type regression alerts, bare except detection, session metrics |
| **memory-check.sh** | Session end | Reminds you to review CLAUDE.md if it hasn't been updated in 90+ days |

### Rules (4)

Context-aware rules that activate when matching files are edited.

| Rule | Activates On | Enforces |
|------|-------------|----------|
| **typescript.md** | `*.ts`, `*.tsx` | Strict typing, no `any`, explicit returns, Zod validation patterns |
| **python.md** | `*.py` | No bare except, type hints, parameterized queries, async patterns |
| **testing.md** | `*.test.*`, `tests/` | TDD workflow, coverage requirements, mocking strategy, AAA pattern |
| **database-migrations.md** | `migrations/` | Naming conventions, rollback requirements, schema conventions, index strategy |

### Documentation (3)

| Document | Purpose |
|----------|---------|
| **ELITE_PRACTICES.md** | Complete guide to elite AI-assisted development (planning, TDD, code review, memory) |
| **ANTI_PATTERNS.md** | Common mistakes with Claude Code and how to avoid them |
| **CONTEXT_OPTIMIZATION.md** | Token management, MCP best practices, session patterns, cost optimization |

### Templates (1)

| Template | Purpose |
|----------|---------|
| **CLAUDE.md.template** | Starter project CLAUDE.md with all toolkit references pre-configured |

---

## Configuration

### settings.example.json

Copy `settings/settings.example.json` to your project's `.claude/settings.json` and customize:

```bash
cp claude-code-toolkit/settings/settings.example.json .claude/settings.json
```

It includes:
- **30+ slash commands** with model routing (haiku for simple tasks, sonnet for features, opus for architecture)
- **Permission patterns** (allow common safe operations, deny dangerous ones)
- **Hook configurations** pointing to the toolkit's hooks

### Customization

Every file is designed to be forked and customized:

1. **Agents**: Edit trigger conditions, add project-specific scope, adjust thresholds
2. **Rules**: Add your project's naming conventions, coverage targets, framework-specific patterns
3. **Hooks**: Modify blocked file patterns, add custom checks, change enforcement modes
4. **Workflows**: Adjust pipeline stages, add/remove agent steps, change gate criteria

---

## Agent Trigger Matrix

### By File Type

| File Pattern | Agents Triggered |
|--------------|------------------|
| `*.ts`, `*.tsx` | type-enforcer, security-hardener |
| `*.py` | security-hardener, documentation-validator |
| `*.sql`, `migrations/*` | db-migration-validator, data-integrity-validator |
| `package.json` | dependency-auditor, bundle-optimizer |
| `.env*`, `*config*` | configuration-validator |
| `src/api/routes/*` | api-contract-generator, security-hardener, impact-analyst |
| `src/services/*` | impact-analyst, modularity-enforcer |
| `docs/*`, `README*` | documentation-validator |

### By Action Type

| Action | Agents Triggered |
|--------|------------------|
| New service creation | observability-architect, modularity-enforcer |
| External API integration | error-resilience-validator, security-hardener |
| Database schema change | db-migration-validator, data-integrity-validator |
| Performance optimization | perf-tuner, database-query-optimizer |
| Pre-deployment review | deployment-strategist, load-testing-designer |
| Security audit | security-hardener, privacy-compliance-auditor, dependency-auditor |

---

## Agent Combinations for Common Tasks

### New Feature Development
1. `modularity-enforcer` -- Architecture review
2. `type-enforcer` -- Type safety
3. `test-contract-author` -- Test coverage
4. `documentation-validator` -- API docs

### Bug Fix
1. `test-analyzer` -- Understand failure
2. `refactor-surgeon` -- Safe fix
3. `test-contract-author` -- Regression tests

### Performance Issue
1. `perf-tuner` -- Profile code
2. `database-query-optimizer` -- Query analysis
3. `cost-optimizer` -- Resource usage

### Security Review
1. `security-hardener` -- Code audit
2. `privacy-compliance-auditor` -- PII check
3. `dependency-auditor` -- CVE scan
4. `configuration-validator` -- Secrets check

### Pre-Production Release
1. `deployment-strategist` -- Rollout plan
2. `load-testing-designer` -- Load scenarios
3. `observability-architect` -- Monitoring
4. `error-resilience-validator` -- Failure modes

---

## Contributing

Contributions are welcome. To add a new agent:

1. Create a markdown file in the appropriate `agents/` subdirectory
2. Follow the existing format (frontmatter with name/description/model, then structured content)
3. Add the agent to `agents/AGENT_INDEX.md`
4. Submit a PR with a description of what the agent does and when it triggers

For other contributions (skills, workflows, hooks, rules), follow the same pattern -- look at existing files for the format, then add your contribution.

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

Built with battle-tested patterns from real-world AI-assisted development. Every agent, hook, and workflow has been refined through thousands of hours of production use.

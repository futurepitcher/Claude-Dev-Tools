# Agent Index

Quick reference for 35 Claude Code specialist agents organized by category.

---

## Code Quality (6 agents)

| Agent | Trigger | Purpose |
|-------|---------|---------|
| `type-enforcer` | TypeScript files | Enforce strict typing, eliminate `any` |
| `refactor-surgeon` | Lint errors, complexity > 10 | Safe, behavior-preserving refactoring |
| `modularity-enforcer` | New services/modules | Ensure loose coupling, dependency injection, DDD compliance |
| `documentation-validator` | API/README changes | Validate docs completeness |
| `accessibility-auditor` | UI components | WCAG 2.1 AA compliance |
| `test-contract-author` | Public API changes | Generate property-based tests |

## Security & Privacy (4 agents)

| Agent | Trigger | Purpose |
|-------|---------|---------|
| `security-hardener` | Auth, routes, deps | Input validation, OWASP Top 10 |
| `privacy-compliance-auditor` | PII handling | GDPR/CCPA, encryption, consent |
| `dependency-auditor` | package.json changes | CVE scanning, license compliance |
| `configuration-validator` | .env, config changes | Secret detection, validation |

## Performance (5 agents)

| Agent | Trigger | Purpose |
|-------|---------|---------|
| `perf-tuner` | Hot paths, critical code | Profile, optimize critical code |
| `perf-monitor` | Performance regressions | Continuous perf tracking |
| `database-query-optimizer` | SQL queries | EXPLAIN plans, index suggestions |
| `cost-optimizer` | Resource-intensive ops | Token usage, caching, batching |
| `bundle-optimizer` | Bundle size increase | Tree-shaking, code splitting |

## Architecture (6 agents)

| Agent | Trigger | Purpose |
|-------|---------|---------|
| `api-contract-generator` | New endpoints | OpenAPI specs, type generation |
| `api-versioning-strategist` | Breaking API changes | Deprecation, migration paths |
| `db-migration-validator` | Schema changes | Safe migrations, rollback plans |
| `data-integrity-validator` | CRUD operations | Constraints, referential integrity |
| `cross-platform-validator` | Shared code | Cross-stack compatibility |
| `component-extraction-planner` | Large components | Decomposition strategy |

## Reliability (4 agents)

| Agent | Trigger | Purpose |
|-------|---------|---------|
| `error-resilience-validator` | External APIs | Circuit breakers, retry logic |
| `concurrency-auditor` | Async/parallel code | Race conditions, deadlocks |
| `observability-architect` | New services | Logging, tracing, metrics |
| `deployment-strategist` | Production deploys | Blue-green, canary, rollback |

## Testing (2 agents)

| Agent | Trigger | Purpose |
|-------|---------|---------|
| `load-testing-designer` | Pre-release | k6/Artillery scenarios |
| `test-analyzer` | Test failures | Root cause analysis |

## Investigation (6 agents)

| Agent | Trigger | Purpose |
|-------|---------|---------|
| `impact-analyst` | Core source files | Dependency tracing, blast radius scoring, breaking change detection |
| `codebase-locator` | "where is X" questions | Find files by pattern |
| `codebase-analyzer` | "how does X work" | Architecture understanding |
| `pattern-finder` | "find examples of" | Similar code patterns |
| `docs-locator` | Documentation search | Find relevant docs |
| `docs-analyzer` | "explain the docs" | Documentation comprehension |

## Research (2 agents)

| Agent | Trigger | Purpose |
|-------|---------|---------|
| `technology-scout` | "what options for" | Research alternatives with weighted scoring |
| `tracer` | Complex bugs, intermittent failures | Evidence-driven causal analysis with competing hypotheses |

## Coordination (1 protocol)

| Agent | Trigger | Purpose |
|-------|---------|---------|
| `coordination-protocol` | Parallel agent execution | File claims, conflict resolution, cross-agent communication |

---

## Auto-Trigger Matrix

### By File Type Changed

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
| Cost review | cost-optimizer, bundle-optimizer |
| Breaking API change | api-versioning-strategist, documentation-validator |

---

## Manual Invocation

Agents can be manually invoked by referencing them:

```
Please run the security-hardener agent on the auth module
```

```
Use the database-query-optimizer to analyze the slow queries in UserRepository
```

```
Run a full quality gate with: type-enforcer, security-hardener, test-contract-author
```

---

## Agent Combinations for Common Tasks

### New Feature Development
1. `modularity-enforcer` - Architecture review
2. `type-enforcer` - Type safety
3. `test-contract-author` - Test coverage
4. `documentation-validator` - API docs

### Bug Fix
1. `test-analyzer` - Understand failure
2. `refactor-surgeon` - Safe fix
3. `test-contract-author` - Regression tests

### Performance Issue
1. `perf-tuner` - Profile code
2. `database-query-optimizer` - Query analysis
3. `cost-optimizer` - Resource usage

### Security Review
1. `security-hardener` - Code audit
2. `privacy-compliance-auditor` - PII check
3. `dependency-auditor` - CVE scan
4. `configuration-validator` - Secrets check

### Pre-Production Release
1. `deployment-strategist` - Rollout plan
2. `load-testing-designer` - Load scenarios
3. `observability-architect` - Monitoring
4. `error-resilience-validator` - Failure modes

### Impact Analysis
1. `impact-analyst` - Blast radius scoring
2. `cross-platform-validator` - If types changed

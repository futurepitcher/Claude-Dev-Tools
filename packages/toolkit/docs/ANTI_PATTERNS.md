# Anti-Patterns to Avoid

> Common mistakes that lead to bugs, technical debt, and wasted effort in Claude Code development.

---

## Memory Mistakes

| Anti-Pattern | Better Approach |
|--------------|-----------------|
| Vague instructions in CLAUDE.md | Specific, actionable rules with examples |
| Never updating CLAUDE.md | Quarterly review cycle |
| Monolithic 500+ line CLAUDE.md | Hierarchical modular structure |
| No memory at all | Invest in memory files upfront |

### Example: Vague vs Specific

```
Vague:  "Format code properly"
Good:   "Use 2-space indentation, Unix line endings, Prettier for TS"

Vague:  "Write clean code"
Good:   "Functions 50 lines, files 300 lines, no nested callbacks >3 deep"
```

---

## Planning Mistakes

| Anti-Pattern | Better Approach |
|--------------|-----------------|
| Jump straight to code | Always `/plan` first for non-trivial work |
| Let AI decide architecture | Define architecture deliberately |
| Ignore existing patterns | Read codebase first, follow patterns |
| Massive PRs | Small, atomic changes |
| No plan approval | Wait for explicit approval |

---

## Testing Mistakes

| Anti-Pattern | Better Approach |
|--------------|-----------------|
| Write tests after code | TDD: tests first |
| Mock everything | Strategic mocking only |
| Trust AI output blindly | Verify everything with tests |
| Skip tests "to move fast" | Tests save time long-term |

---

## Code Quality Mistakes

| Anti-Pattern | Better Approach |
|--------------|-----------------|
| Use `any` type | Use `unknown` + type guards |
| Bare `except:` | Specify exception type |
| Over-engineer "just in case" | Minimum viable implementation |
| Premature abstraction | Three instances before abstracting |
| God objects/functions | Single responsibility |

---

## Architecture Mistakes

| Anti-Pattern | Better Approach |
|--------------|-----------------|
| UI calling database directly | UI -> API -> Service -> Repository -> DB |
| Circular imports | Clear dependency direction |
| Hardcoded secrets | Environment variables + keychain |
| Skip the API layer | Single entry point |
| Monolithic files | Focused files with clear purpose |

---

## Session Mistakes

| Anti-Pattern | Better Approach |
|--------------|-----------------|
| Never clearing context | `/clear` between unrelated tasks |
| No handoff documents | Create handoffs for WIP |
| Using wrong model | Match model to task complexity |

---

## Security Anti-Patterns

| Anti-Pattern | Better Approach |
|--------------|-----------------|
| Hardcoded credentials | Environment variables + keychain |
| String SQL concatenation | Parameterized queries |
| No input validation | Validate at boundaries |
| Logging PII | Sanitize logs |
| Trusting user input | Always validate, sanitize, escape |

---

## Quick Self-Check

Before committing, ask:
- [ ] Did I plan before coding?
- [ ] Are there any `any` types or bare `except:`?
- [ ] Did I test my changes?
- [ ] Did I follow existing patterns?
- [ ] Are there any hardcoded secrets?
- [ ] Did I verify Claude's output?

---

*When in doubt, prefer simplicity. The best code is code you don't have to debug.*

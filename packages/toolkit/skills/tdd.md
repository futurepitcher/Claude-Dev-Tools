# Skill: TDD Workflow

> RED-GREEN-REFACTOR cycle with optional phase gate enforcement via hooks.

## When to Use

- Any code change that can be tested
- Bug fixes (always test-first)
- Refactoring existing code

## Workflow

### 1. RED Phase — Write Failing Test

- Write a test that captures the desired behavior
- Run it — confirm it fails for the right reason
- Test should be small (2-10 minute implementation target)

### 2. GREEN Phase — Make It Pass

- Write the minimum code to make the test pass
- No refactoring, no optimization, no "while I'm here"
- Run test — confirm it passes

### 3. REFACTOR Phase — Clean Up

- Improve code quality while keeping tests green
- Extract methods, rename variables, reduce duplication
- Run tests after each change — they must stay green

### 4. Repeat

Each RED-GREEN-REFACTOR cycle should be 2-10 minutes.
For larger features, break into multiple small cycles.

## Hook Enforcement

When TDD enforcement is active via hooks:
- **RED**: pre-tool.sh blocks edits to non-test files
- **GREEN**: all edits allowed
- **REFACTOR**: all edits allowed (tests must pass after each change)

## Why TDD with AI

TDD is especially powerful with Claude Code because:
1. Tests define clear, verifiable requirements
2. Claude fulfills specific test expectations
3. Edge cases are explicitly documented
4. Reduces AI-generated bugs significantly

## Edge Case Tests First

```typescript
describe('validateAge', () => {
  it('should reject negative ages', () =>
    expect(validateAge(-5)).toThrow('Age must be positive'));
  it('should accept zero', () =>
    expect(validateAge(0)).toBe(0));
  it('should accept normal range', () =>
    expect(validateAge(35)).toBe(35));
  it('should reject unrealistic ages', () =>
    expect(validateAge(200)).toThrow('Age exceeds maximum'));
  it('should reject NaN', () =>
    expect(validateAge(NaN)).toThrow('Invalid age'));
});
```

Claude will fulfill these specific requirements, reducing bugs.

## Integration

- Invoked by: `/tdd`, `/refactor`, `/enforce tdd`
- Hooks: pre-tool.sh (phase gate enforcement)

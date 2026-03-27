---
paths: ["**/*.test.ts", "**/*.test.tsx", "**/tests/**", "**/__tests__/**", "**/test_*.py", "**/*_test.py"]
---
# Testing Rules

## TDD Workflow (CRITICAL)

**Always write tests BEFORE implementation.**

```
RED      Write failing test first
         Define expected behavior with edge cases

GREEN    Write minimal code to pass test
         No more, no less

REFACTOR Clean up while tests pass
         Remove duplication

         REPEAT
```

### Why TDD with AI

TDD is especially powerful with Claude Code because:
1. Tests define clear, verifiable requirements
2. Claude fulfills specific test expectations
3. Edge cases are explicitly documented
4. Reduces AI-generated bugs significantly

### Edge Case Tests First

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

## Test Structure
- Use Arrange-Act-Assert (AAA) pattern
- One assertion per test when possible
- Descriptive test names: `should_return_error_when_user_not_found`
- Group related tests with `describe` blocks

## Jest/Vitest (TypeScript)
- Use `describe`/`it` pattern
- Mock external dependencies with `jest.mock()`
- Use `beforeEach`/`afterEach` for setup/teardown
- Prefer `toEqual` over `toBe` for objects
- Use `toMatchSnapshot` sparingly

## Pytest (Python)
- Use fixtures for common setup
- Mark slow tests: `@pytest.mark.slow`
- Mark integration tests: `@pytest.mark.integration`
- Use parametrize for data-driven tests

## Coverage Requirements
- Critical paths (auth, payments, data access): 90%+
- Business logic (services): 80%+
- Utilities and helpers: 70%+
- New code must not decrease overall coverage

## Mocking Strategy
- Mock at service boundaries, not internal functions
- Never mock the thing you're testing
- Use realistic mock data
- Reset mocks between tests
- Document why each mock exists

## Integration Testing
- Test actual database operations (use test DB)
- Test API endpoints with supertest/httpx
- Test cross-service communication
- Clean up test data after each test

## Test Data
- Use factories for complex objects
- Keep test data minimal but realistic
- Never use production data in tests
- Seed random data deterministically

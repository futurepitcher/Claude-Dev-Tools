---
paths: ["**/*.ts", "**/*.tsx"]
---
# TypeScript Rules

## Critical Constraints (NEVER Violate)

- **NEVER** use `any` type — use `unknown`, generics, or proper interfaces
- **NEVER** use `as any` type assertions
- **NEVER** use `var` — only `const` or `let`
- **NEVER** leave `console.log` in production code
- **NEVER** create circular dependencies between modules

## Type Safety

### Replace `any` with Proper Types
```typescript
// BAD
function process(data: any): any { return data.value; }

// GOOD
function process(data: unknown): string {
  if (isRecord(data) && typeof data.value === 'string') {
    return data.value;
  }
  throw new Error('Invalid data');
}
```

### Use Discriminated Unions
```typescript
// BAD
interface Event { type: string; payload: any; }

// GOOD
type Event =
  | { type: 'created'; payload: { id: string } }
  | { type: 'deleted'; payload: { id: string } };
```

### Explicit Return Types on Public Functions
```typescript
// BAD
export function getUser(id: string) { /* ... */ }

// GOOD
export function getUser(id: string): Promise<User | null> { /* ... */ }
```

### Zod for Runtime Validation (External Data)
```typescript
import { z } from 'zod';

const UserSchema = z.object({
  id: z.string(),
  email: z.string().email(),
  role: z.enum(['admin', 'user']),
});

type User = z.infer<typeof UserSchema>;
```

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Variables/Functions | camelCase | `getUserById` |
| Classes/Types | PascalCase | `UserService` |
| Constants | UPPER_SNAKE | `MAX_RETRIES` |
| Files (classes) | PascalCase.ts | `UserService.ts` |
| Files (utils) | camelCase.ts | `formatDate.ts` |

## ESLint Rules (Recommended)

```json
{
  "@typescript-eslint/no-explicit-any": "error",
  "@typescript-eslint/explicit-function-return-type": "warn",
  "@typescript-eslint/no-unsafe-assignment": "error",
  "@typescript-eslint/no-unused-vars": "error",
  "no-console": "error"
}
```

## Import Organization

1. External packages (node_modules)
2. Internal absolute imports (@/...)
3. Relative imports (./...)
4. Type-only imports (import type { ... })

## Error Handling

- Use typed error classes, not generic Error
- Always catch specific error types
- Never swallow errors silently
- Log errors with context (what operation failed, with what input)

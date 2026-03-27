---
paths: ["**/*.py"]
---
# Python Rules

## Critical Constraints (NEVER Violate)

- **NEVER** use bare `except:` — always specify exception type
- **NEVER** use `from module import *`
- **NEVER** ignore type hints in public functions
- **NEVER** use mutable default arguments
- **NEVER** use string concatenation for SQL queries

## Exception Handling

```python
# BAD - bare except catches everything including KeyboardInterrupt
try:
    result = process()
except:
    pass

# GOOD - specific exception type
try:
    result = process()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise
except (IOError, OSError) as e:
    logger.warning(f"I/O error: {e}")
    return default_value
```

## Type Hints

```python
# BAD - no type hints
def get_user(user_id):
    ...

# GOOD - full type hints on public functions
def get_user(user_id: str) -> Optional[User]:
    ...

# GOOD - type hints with generics
def find_items(query: str, limit: int = 10) -> list[Item]:
    ...
```

## Mutable Default Arguments

```python
# BAD - mutable default is shared across calls
def add_item(items: list = []):
    items.append("new")
    return items

# GOOD - use None sentinel
def add_item(items: list | None = None) -> list:
    if items is None:
        items = []
    items.append("new")
    return items
```

## SQL Safety

```python
# BAD - SQL injection vulnerability
query = f"SELECT * FROM users WHERE id = {user_id}"

# GOOD - parameterized query
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))
```

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Variables/Functions | snake_case | `get_user_by_id` |
| Classes | PascalCase | `UserService` |
| Constants | UPPER_SNAKE | `MAX_RETRIES` |
| Files | snake_case.py | `user_service.py` |
| Private | _leading_underscore | `_internal_helper` |

## Async Patterns

```python
# Use asyncio for I/O-bound work
async def fetch_all(urls: list[str]) -> list[Response]:
    async with aiohttp.ClientSession() as session:
        return await asyncio.gather(
            *[fetch(session, url) for url in urls]
        )

# Use multiprocessing for CPU-bound work
from multiprocessing import Pool

with Pool(processes=4) as pool:
    results = pool.map(cpu_bound_work, data_chunks)
```

## Testing

- Use pytest fixtures for common setup
- Mark slow tests: `@pytest.mark.slow`
- Use `@pytest.mark.parametrize` for data-driven tests
- Prefer explicit assertions over bare `assert`

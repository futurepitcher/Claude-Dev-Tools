---
paths: ["**/migrations/**", "**/database/migrations/**"]
---
# Database Migration Rules

## Migration Naming
- Format: `NNN_descriptive_name.ts` or `NNN_descriptive_name.py`
- Increment NNN sequentially (e.g., 039, 040, 041)
- Use snake_case for description
- Be specific: `add_user_preferences_table` not `update_db`

## Migration Safety (CRITICAL)
- EVERY migration must have a rollback/down function
- NEVER drop columns in production without data backup
- NEVER rename columns directly — add new, migrate data, then drop old
- Test rollback before committing migration
- Include estimated execution time in comments

## Schema Conventions
- Column names: `snake_case`
- Table names: `snake_case`, plural (`users`, `order_items`)
- Primary keys: `id` (INTEGER AUTOINCREMENT for SQLite)
- Foreign keys: `<table_singular>_id` (`user_id`, `project_id`)
- Timestamps: `created_at`, `updated_at` (ISO 8601)
- Boolean columns: `is_<adjective>` (`is_active`, `is_deleted`)

## Index Strategy
- Index all foreign keys
- Index columns used in WHERE clauses
- Index columns used in ORDER BY
- Use composite indexes for multi-column queries
- Document why each index exists

## Data Integrity
- Use foreign key constraints
- Add NOT NULL where appropriate
- Use CHECK constraints for enums
- Add DEFAULT values for optional columns
- Use UNIQUE constraints to prevent duplicates

## Dangerous Patterns to Avoid

```sql
-- DANGEROUS: INSERT OR REPLACE on tables with CASCADE foreign keys
-- This silently deletes all child rows!
INSERT OR REPLACE INTO parents (id, name) VALUES (1, 'updated');
-- Use UPDATE for existing rows instead

-- DANGEROUS: Adding NOT NULL without default
ALTER TABLE users ADD COLUMN role TEXT NOT NULL;
-- SAFE: Add with default
ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'user';

-- DANGEROUS: Dropping column directly
ALTER TABLE users DROP COLUMN email;
-- SAFE: Add new, migrate, then drop old (across multiple deploys)
```

## Testing Migrations
- Test on copy of production data
- Verify data integrity after migration
- Check query performance with EXPLAIN
- Test with edge cases (NULL values, large datasets)
- Document any manual steps required

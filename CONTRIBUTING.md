# Contributing to REPA

Thank you for contributing to REPA! This guide will help you get started.

## Git Status Colors Explained

When you run `git status`, you'll see files in different colors:

- **🟢 Green (staged)**: Files that are added and ready to commit (`git add`)
- **🟡 Yellow (modified/unstaged)**: Files that have been changed but not yet staged
- **🔴 Red (untracked)**: New files that Git doesn't know about yet
- **⚪ White**: Files that are up to date (no changes)

## Pre-Commit Checklist

Before committing your changes, make sure to:

### 1. Review Your Changes
```bash
# See what files have changed
git status

# See the actual changes in each file
git diff
```

### 2. Stage Files Selectively
```bash
# Add specific files (recommended)
git add app.py
git add static/profile.html
git add README.md

# Or add all changes (use with caution)
git add .
```

### 3. Review Staged Changes
```bash
# See what will be committed
git diff --staged
```

### 4. Commit with a Clear Message
```bash
git commit -m "Add email monitoring feature with configurable filters"
```

### 5. Push to Remote
```bash
git push origin main
```

## What NOT to Commit

**Never commit:**
- `.env` files (contains secrets)
- `__pycache__/` directories
- `.DS_Store` files
- Log files (`*.log`)
- Virtual environment folders (`venv/`, `.venv/`)
- IDE configuration files (`.vscode/`, `.idea/`)

These are already in `.gitignore` and will be automatically excluded.

## Commit Message Guidelines

Write clear, descriptive commit messages:

**Good:**
- "Add email monitoring with configurable sender and subject filters"
- "Fix RLS policy errors by using service role key for backend operations"
- "Update profile page to display collapsible email analysis results"

**Bad:**
- "fix stuff"
- "updates"
- "changes"

## Branch Strategy

- **main**: Production-ready code
- **feature/**: New features (e.g., `feature/email-notifications`)
- **fix/**: Bug fixes (e.g., `fix/url-extraction`)

## Testing Before Committing

1. **Run the server locally:**
   ```bash
   python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Test your changes:**
   - Test the feature you added/modified
   - Check for errors in the console
   - Verify database operations work correctly

3. **Check for linting errors:**
   ```bash
   # If you have a linter configured
   pylint app.py
   ```

## Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add comments for complex logic
- Keep functions focused and small

## Database Changes

If you modify the database schema:

1. Create a migration SQL file: `supabase_schema_feature_name.sql`
2. Document the changes in `CHANGES.md`
3. Update `README.md` if needed
4. Test the migration on a development database first

## Questions?

If you're unsure about something:
1. Check existing code for patterns
2. Review `README.md` and `CHANGES.md`
3. Ask your team before committing


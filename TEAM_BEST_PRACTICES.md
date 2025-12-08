# 🎯 Team Best Practices - REPA Repository

## 📋 Pre-Commit Checklist

Before committing any changes, ensure you've completed these steps:

### 1. Code Quality ✅
- [ ] Code runs without errors locally
- [ ] Tested all affected features
- [ ] No console errors in browser
- [ ] Code follows existing patterns and style
- [ ] Removed debug `print()` statements or commented code

### 2. Security 🔒
- [ ] **Never commit `.env` files** (already in `.gitignore`)
- [ ] No hardcoded API keys, passwords, or secrets
- [ ] Database operations use proper authentication (service role key for backend)
- [ ] Sensitive data is excluded from responses (e.g., `email_app_password`)

### 3. Documentation 📚
- [ ] Updated `README.md` if features changed
- [ ] Updated `CHANGES.md` with new changes
- [ ] Added inline comments for complex logic
- [ ] Updated API endpoint documentation if changed

### 4. Database Changes 🗄️
- [ ] Created migration SQL files if schema changed
- [ ] Tested migrations in development
- [ ] Updated RLS policies if needed
- [ ] Documented migration steps in `DATABASE_MIGRATION_GUIDE.md`

### 5. Git Workflow 🔄
- [ ] Reviewed changes: `git diff`
- [ ] Staged only relevant files (not logs, cache, temp files)
- [ ] Commit message follows format: `type: brief description`
- [ ] Branch is up to date: `git pull origin main`

## 📝 Commit Message Format

Use clear, descriptive commit messages:

```
type: brief description (50 chars max)

Optional longer description explaining:
- What changed
- Why it changed
- Any breaking changes
```

### Commit Types:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

### Examples:
```
feat: Add email monitoring with configurable filters

- Added sender and subject keyword filtering
- Support for multiple URLs per email
- Background task runs every 5 minutes
- Stores analysis results in database

fix: Resolve RLS issues with service role key

- Use SUPABASE_SERVICE_KEY for backend operations
- Properly bypass RLS for admin operations
- Fix user criteria retrieval

docs: Update README with email monitoring setup
```

## 🚫 What NOT to Commit

**Never commit these files:**
- `.env` and `.env.*` files (contains secrets)
- `__pycache__/` directories
- `*.log` files
- `*.pyc` files
- `.DS_Store` (macOS)
- Temporary files (`*.tmp`, `*.bak`)
- IDE configuration (`.vscode/`, `.idea/`)

**Check `.gitignore` is up to date!**

## 🔍 Review Before Committing

```bash
# 1. Check what changed
git status

# 2. Review actual changes
git diff

# 3. Review staged changes
git diff --staged

# 4. Check for secrets (run this before staging)
grep -r "API_KEY\|PASSWORD\|SECRET" --include="*.py" --include="*.html" --include="*.js" | grep -v ".env"

# 5. Check file sizes (avoid committing large files)
find . -type f -size +1M -not -path "./.git/*"
```

## 🌿 Branch Strategy

- **`main`** - Production-ready code only
- **`develop`** - Integration branch for features (if using)
- **`feature/feature-name`** - New features
- **`fix/bug-name`** - Bug fixes

## 📦 Before Pushing

1. **Pull latest changes:**
   ```bash
   git pull origin main
   ```

2. **Resolve any conflicts**

3. **Test again after merge**

4. **Push:**
   ```bash
   git push origin main
   ```

## 🧪 Testing Checklist

Before committing, test:
- [ ] Server starts without errors
- [ ] Authentication works (login/register)
- [ ] Chat endpoint processes messages
- [ ] Profile page saves/loads criteria
- [ ] Email monitoring (if changed)
- [ ] Database operations work
- [ ] No console errors in browser

## 📊 Code Review Guidelines

When reviewing PRs:
- Check for security issues
- Verify error handling
- Ensure consistent code style
- Test the changes locally
- Check documentation is updated

## 🔧 Environment Setup

Ensure team members have:
- Python 3.8+ installed
- `.env` file configured (not committed)
- Supabase project set up
- Database migrations run
- Dependencies installed: `pip install -r requirements.txt`

## 📞 Communication

- Document breaking changes in `CHANGES.md`
- Note required environment variables
- List new dependencies in `requirements.txt`
- Update setup guides if needed

## 🎓 First Time Setup

New team members should:
1. Clone repository
2. Read `README.md`
3. Follow `SETUP.md`
4. Run database migrations
5. Configure `.env` file
6. Test locally

---

**Remember:** When in doubt, ask! Better to clarify than commit broken code.


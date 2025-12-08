# Pre-Commit Checklist

Use this checklist before committing changes to ensure code quality and team readiness.

## ✅ Code Quality

- [ ] Code runs without errors
- [ ] Tested locally (server starts, features work)
- [ ] No console errors in browser
- [ ] No linting errors
- [ ] Code follows existing patterns

## ✅ Security

- [ ] No secrets committed (check `.env` is in `.gitignore`)
- [ ] No hardcoded API keys or passwords
- [ ] Database operations use service role key (backend) or RLS (frontend)

## ✅ Documentation

- [ ] Updated `README.md` if features changed
- [ ] Updated `CHANGES.md` with new changes
- [ ] Added comments for complex code
- [ ] Updated API documentation if endpoints changed

## ✅ Database

- [ ] Database migrations tested
- [ ] Migration files created if schema changed
- [ ] RLS policies updated if needed

## ✅ Git

- [ ] Reviewed changes with `git diff`
- [ ] Staged only relevant files (not `.env`, logs, etc.)
- [ ] Commit message is clear and descriptive
- [ ] Branch is up to date with `main`

## ✅ Team Communication

- [ ] Documented breaking changes
- [ ] Noted any required environment variables
- [ ] Listed dependencies that need installation
- [ ] Provided setup instructions if needed

## Quick Commands

```bash
# 1. Check status
git status

# 2. Review changes
git diff

# 3. Stage files
git add app.py static/profile.html README.md

# 4. Review staged changes
git diff --staged

# 5. Commit
git commit -m "Clear description of changes"

# 6. Push
git push origin main
```


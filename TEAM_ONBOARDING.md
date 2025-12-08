# Team Onboarding Guide

Welcome to the REPA project! This guide will help you get started.

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd repa
   ```

2. **Set up Python environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env  # If exists, or create new .env file
   # Edit .env and add your API keys
   ```

4. **Set up Supabase database:**
   - Run `supabase_schema.sql` in Supabase SQL Editor
   - Run `supabase_schema_email.sql`
   - Run `supabase_schema_property_type.sql`
   - Run `supabase_schema_email_filters.sql`

5. **Start the server:**
   ```bash
   python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```

6. **Open in browser:**
   ```
   http://localhost:8000
   ```

## Project Structure

```
repa/
├── app.py                          # Main FastAPI backend
├── static/
│   ├── index.html                 # Chat interface
│   └── profile.html               # User profile page
├── requirements.txt               # Python dependencies
├── .env                          # Environment variables (NOT committed)
├── .gitignore                    # Git ignore rules
├── supabase_schema*.sql          # Database migrations
├── README.md                     # Main documentation
├── CHANGES.md                    # Changelog
├── CONTRIBUTING.md               # Contribution guidelines
└── PRE_COMMIT_CHECKLIST.md      # Pre-commit checklist
```

## Key Features

1. **Chat Interface**: Users describe their apartment needs and optionally include a listing URL
2. **User Profiles**: Save and manage apartment criteria
3. **Email Monitoring**: Automatically check emails for new listings and analyze them
4. **Authentication**: Supabase Auth with JWT tokens

## Important Files

- **`app.py`**: Backend API endpoints and business logic
- **`static/index.html`**: Frontend chat interface
- **`static/profile.html`**: User profile and settings page
- **`.env`**: Your API keys (NEVER commit this!)

## Environment Variables

Required in `.env`:
- `OPENAI_API_KEY`
- `FIRECRAWL_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SUPABASE_SERVICE_KEY`

## Database Schema

The project uses Supabase (PostgreSQL) with these main tables:
- `user_criteria`: User apartment preferences
- `processed_emails`: Email analysis results

See `supabase_schema*.sql` files for details.

## Common Issues

### "Email monitoring not finding emails"
- Emails must be **UNSEEN** (unread)
- Check sender filter matches exactly
- Check subject keywords match

### "RLS policy error"
- Backend uses `SUPABASE_SERVICE_KEY` (service role)
- Frontend uses `SUPABASE_KEY` (anon key) with JWT

### "No analyses showing"
- Check server logs: `tail -f /tmp/server.log`
- Verify email was processed
- Check database for `processed_emails` records

## Development Workflow

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make changes
3. Test locally
4. Review with `git diff`
5. Stage files: `git add <files>`
6. Commit: `git commit -m "Clear message"`
7. Push: `git push origin feature/my-feature`
8. Create pull request

## Getting Help

- Check `README.md` for setup instructions
- Check `CHANGES.md` for recent updates
- Check `CONTRIBUTING.md` for contribution guidelines
- Review code comments in `app.py`

## Testing Checklist

Before committing:
- [ ] Server starts without errors
- [ ] Can register/login
- [ ] Can save criteria in profile
- [ ] Chat interface works
- [ ] Email monitoring works (if configured)
- [ ] No console errors

## Questions?

Ask your team lead or check the documentation files!


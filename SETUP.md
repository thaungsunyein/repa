# REPA Setup Guide - Supabase Authentication

This guide will help you set up Supabase authentication for the REPA application.

## Prerequisites

1. A Supabase account (sign up at https://supabase.com)
2. Python 3.8+ installed
3. All existing API keys (OpenAI, Firecrawl)

## Step 1: Create Supabase Project

1. Go to https://supabase.com and sign in
2. Click "New Project"
3. Fill in:
   - **Name**: REPA (or your preferred name)
   - **Database Password**: Choose a strong password (save this!)
   - **Region**: Choose closest to you
4. Click "Create new project" and wait for setup to complete (~2 minutes)

## Step 2: Get Supabase Credentials

1. In your Supabase project dashboard, go to **Settings** → **API**
2. Copy the following values:
   - **Project URL** (SUPABASE_URL)
   - **anon public** key (SUPABASE_KEY)
   - **service_role** key (SUPABASE_SERVICE_KEY) - Keep this secret!

## Step 3: Create Database Table

1. In Supabase dashboard, go to **SQL Editor**
2. Click "New query"
3. Copy and paste the contents of `supabase_schema.sql`
4. Click "Run" to execute the SQL
5. Verify the table was created by going to **Table Editor** → you should see `user_criteria`

## Step 4: Configure Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Firecrawl API Key
FIRECRAWL_API_KEY=your_firecrawl_api_key_here

# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_KEY=your_supabase_service_role_key_here

# JWT Secret (optional, defaults to SUPABASE_KEY if not set)
JWT_SECRET=your_jwt_secret_here

# Server Port (optional, defaults to 8000)
PORT=8000
```

Replace the placeholder values with your actual keys.

## Step 5: Install Dependencies

```bash
uv
```

## Step 6: Run the Application

**Option 1: Using Python directly**
```bash
python3 app.py
```

**Option 2: Using uvicorn directly (recommended)**
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The app will start at http://localhost:8000

**Note:** On macOS and Linux, use `python3` instead of `python`. If you get a "command not found" error, make sure Python 3 is installed.

## Step 7: Test Authentication

1. Open http://localhost:8000 in your browser
2. You should see a login modal
3. Click "Register" to create a new account
4. After registration/login, you'll be able to access the chat interface
5. Click "Profile" in the header to save your apartment criteria

## Database Schema

The `user_criteria` table stores:
- `id`: UUID primary key
- `user_id`: References auth.users (from Supabase Auth)
- `location`: Text field for location preference
- `min_rooms`, `max_rooms`: Integer fields for room count range
- `min_living_space`, `max_living_space`: Decimal fields for space range (m²)
- `min_rent`, `max_rent`: Decimal fields for rent range (CHF)
- `occupants`: Integer for number of people
- `duration`: Text field (e.g., "ski season", "6 months")
- `starting_when`: Text field for move-in timing
- `user_additional_requirements`: JSONB field for flexible additional requirements
- `created_at`, `updated_at`: Timestamps

## Security Notes

- The `SUPABASE_SERVICE_KEY` has admin privileges - never expose it in client-side code
- Row Level Security (RLS) is enabled - users can only access their own criteria
- JWT tokens expire after 24 hours by default
- Passwords are hashed by Supabase Auth automatically

## Troubleshooting

### "SUPABASE_URL and SUPABASE_KEY must be set"
- Make sure your `.env` file exists and contains the correct values
- Check that variable names match exactly (case-sensitive)

### "Registration failed" or "Login failed"
- Verify your Supabase credentials are correct
- Check Supabase project status in dashboard
- Ensure email confirmation is disabled (Settings → Auth → Email Auth → Confirm email)

### "No criteria found for user"
- This is normal for new users - use the Profile page to create criteria

### Database connection errors
- Verify your Supabase project is active
- Check that the SQL schema was executed successfully
- Ensure RLS policies are enabled

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user

### User Criteria (Protected)
- `GET /api/user/criteria` - Get user's criteria
- `POST /api/user/criteria` - Create/update user's criteria
- `PUT /api/user/criteria` - Update user's criteria

### Chat (Protected)
- `POST /api/chat` - Process chat message (requires JWT token)

All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Next Steps

- Customize the authentication flow if needed
- Add email verification if required
- Implement password reset functionality
- Add user profile management features



# 🚀 Complete Setup Guide - REPA Application

This guide will walk you through **everything** you need to do to get REPA up and running with all the new features.

---

## 📋 Prerequisites Checklist

Before starting, make sure you have:
- [ ] Python 3.8+ installed
- [ ] A Supabase account (free tier works)
- [ ] OpenAI API key
- [ ] Firecrawl API key (free tier available)
- [ ] A code editor (VS Code, etc.)

---

## Step 1: Database Setup (Supabase)

### 1.1 Create Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Click **"New Project"**
3. Fill in:
   - **Name**: REPA (or your preferred name)
   - **Database Password**: Choose a strong password (save this!)
   - **Region**: Choose closest to you
4. Click **"Create new project"** and wait ~2 minutes

### 1.2 Get Supabase Credentials

1. In your Supabase project dashboard, go to **Settings** → **API**
2. Copy these values (you'll need them later):
   - **Project URL** (looks like: `https://xxxxx.supabase.co`)
   - **anon public** key (long string starting with `eyJ...`)
   - **service_role** key (long string, keep this secret!)

### 1.3 Create Base Tables

1. Go to **SQL Editor** in the left sidebar
2. Click **"New query"**
3. Open `supabase_schema.sql` from your project
4. **Copy ALL the SQL** and paste into the editor
5. Click **"Run"** (or press `Ctrl+Enter`)
6. ✅ You should see "Success" message

**Verify:** Go to **Table Editor** → You should see `user_criteria` table

### 1.4 Add Email Monitoring Tables

1. Go back to **SQL Editor**
2. Click **"New query"** again
3. Open `supabase_schema_email.sql` from your project
4. **Copy ALL the SQL** and paste into the editor
5. Click **"Run"**
6. ✅ Success!

**Verify:** Go to **Table Editor** → You should see `processed_emails` table

### 1.5 Add Property Type Field

1. Go to **SQL Editor** → **New query**
2. Open `supabase_schema_property_type.sql`
3. **Copy ALL the SQL** and paste
4. Click **"Run"**
5. ✅ Success!

**Verify:** In `user_criteria` table, you should see `property_type` column

### 1.6 Add Email Filter Fields

1. Go to **SQL Editor** → **New query**
2. Open `supabase_schema_email_filters.sql`
3. **Copy ALL the SQL** and paste
4. Click **"Run"**
5. ✅ Success!

**Verify:** In `user_criteria` table, you should see:
- ✅ `email_sender` column
- ✅ `email_subject_keywords` column

---

## Step 2: Environment Variables Setup

### 2.1 Create .env File

1. In your project root directory (`/Users/gildafernandezconchajahnsen/repa`), create a file named `.env`
2. Open it in your text editor

### 2.2 Add All Required Variables

Copy this template and fill in your actual values:

```env
# OpenAI API Key
OPENAI_API_KEY=sk-your-openai-api-key-here

# Firecrawl API Key
FIRECRAWL_API_KEY=fc-your-firecrawl-api-key-here

# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_KEY=your_supabase_service_role_key_here

# Optional - JWT Secret (defaults to SUPABASE_KEY if not set)
JWT_SECRET=your_jwt_secret_here

# Optional - Server Port (defaults to 8000)
PORT=8000

# Optional - CORS Origins (comma-separated, leave empty for default)
CORS_ORIGINS=http://localhost:8000,https://your-domain.com
```

### 2.3 Get Your API Keys

**OpenAI API Key:**
1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Sign in or create account
3. Click **"Create new secret key"**
4. Copy the key (starts with `sk-`)
5. Paste into `.env` file

**Firecrawl API Key:**
1. Go to [https://firecrawl.dev](https://firecrawl.dev)
2. Sign up for free account
3. Go to **Dashboard** → **API Keys**
4. Copy your API key
5. Paste into `.env` file

**Supabase Keys:**
- Use the keys you copied in Step 1.2
- `SUPABASE_URL`: Your project URL
- `SUPABASE_KEY`: The anon public key
- `SUPABASE_SERVICE_KEY`: The service_role key (keep secret!)

### 2.4 Save .env File

1. Save the `.env` file
2. **Important:** Make sure `.env` is in `.gitignore` (don't commit it to git!)

---

## Step 3: Install Dependencies

### 3.1 Open Terminal

1. Open Terminal/Command Prompt
2. Navigate to your project directory:
   ```bash
   cd /Users/gildafernandezconchajahnsen/repa
   ```

### 3.2 Install Python Packages

Run this command:

```bash
pip3 install -r requirements.txt
```

**Expected output:** You should see packages being installed

**If you get errors:**
- Try: `python3 -m pip install -r requirements.txt`
- Or: `pip install -r requirements.txt`

### 3.3 Verify Installation

Check that key packages are installed:

```bash
python3 -c "import fastapi; import supabase; import openai; print('All packages installed!')"
```

✅ Should print: "All packages installed!"

---

## Step 4: Test Database Connection

### 4.1 Quick Test Script

Create a test file to verify Supabase connection:

```bash
python3 -c "
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

if url and key:
    supabase = create_client(url, key)
    print('✅ Supabase connection successful!')
else:
    print('❌ Missing SUPABASE_URL or SUPABASE_KEY in .env')
"
```

✅ Should print: "✅ Supabase connection successful!"

---

## Step 5: Run the Application

### 5.1 Start the Server

**Option 1: Using Python directly**
```bash
python3 app.py
```

**Option 2: Using uvicorn (recommended)**
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

**Expected output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 5.2 Verify Server is Running

1. Open your browser
2. Go to [http://localhost:8000](http://localhost:8000)
3. ✅ You should see the REPA login page

---

## Step 6: Create Your First User Account

### 6.1 Register

1. On the login page, click **"Sign up"** (or "Register")
2. Enter:
   - **Email**: your.email@example.com
   - **Password**: (choose a secure password)
3. Click **"Sign Up"**
4. ✅ You should be logged in and see the chat interface

### 6.2 Verify Authentication

- ✅ You should see "Logged in as: your.email@example.com" in the header
- ✅ The chat interface should be visible
- ✅ You should see a "Profile" link in the header

---

## Step 7: Configure Your Profile

### 7.1 Open Profile Page

1. Click **"Profile"** in the header (or go to [http://localhost:8000/profile](http://localhost:8000/profile))
2. ✅ Profile form should load

### 7.2 Fill in Apartment Criteria

Fill in your preferences:
- **Property Type**: Select "Rent" or "Buy"
- **Location**: e.g., "Zürich" or "8008 Zürich"
- **Min/Max Rooms**: e.g., 3-5 rooms
- **Min/Max Living Space**: e.g., 80-120 m²
- **Min/Max Rent**: e.g., 2000-4000 CHF
- **Occupants**: Number of people
- **Duration**: e.g., "long-term" or "6 months"

### 7.3 Configure Email Monitoring (Optional)

If you want automatic email monitoring:

1. Check **"Enable Email Monitoring"**
2. **Email Address**: Enter the email that receives listing notifications
3. **Email Provider**: Select your provider (Gmail, Outlook, etc.)
4. **Email Sender Filter**: Enter sender name (e.g., "homegate") or leave empty for default
5. **Subject Keywords**: Enter keywords (e.g., "match,new listing") or leave empty for default "match"
6. **App Password**: Enter your app-specific password (see instructions below)

### 7.4 Get App-Specific Password

**For Gmail:**
1. Go to [Google Account](https://myaccount.google.com/)
2. **Security** → **2-Step Verification** (must be enabled)
3. Scroll to **App passwords**
4. Generate password for "Mail"
5. Copy the 16-character password

**For Outlook:**
1. Go to [Microsoft Account Security](https://account.microsoft.com/security)
2. **Advanced security options** → **App passwords**
3. Create new app password
4. Copy the password

### 7.5 Save Criteria

1. Click **"Save Criteria"** button
2. ✅ You should see "Criteria saved successfully!" message

---

## Step 8: Test the Application

### 8.1 Test Manual Analysis

1. Go back to the main chat page ([http://localhost:8000](http://localhost:8000))
2. Type a message like:
   ```
   I'm looking to rent a 3-room apartment in Zürich, max CHF 3000, with parking.
   Check this listing: https://www.homegate.ch/rent/4002583790
   ```
3. Click **"Send"**
4. ✅ Wait 10-15 seconds
5. ✅ You should see a detailed match analysis with:
   - Match score
   - Listing summary
   - What matches/doesn't match
   - Recommendation
   - Images (if available)

### 8.2 Test Profile Page

1. Go to Profile page
2. ✅ Your saved criteria should be loaded
3. ✅ Property type dropdown should work
4. ✅ Email monitoring fields should be visible

### 8.3 Test Email Monitoring (If Configured)

1. In Profile page, click **"Check Email Now"** button
2. ✅ Should see "Email check started!" message
3. Check server logs for any errors

---

## Step 9: Verify Everything Works

### Checklist:

- [ ] ✅ Server starts without errors
- [ ] ✅ Login/Register works
- [ ] ✅ Profile page loads and saves criteria
- [ ] ✅ Property type field appears and saves
- [ ] ✅ Email monitoring fields appear and save
- [ ] ✅ Manual chat analysis works
- [ ] ✅ Match reports are generated correctly
- [ ] ✅ Images are analyzed (if listing has images)

---

## Troubleshooting Common Issues

### Issue: "SUPABASE_URL and SUPABASE_KEY must be set"

**Solution:**
- Check your `.env` file exists
- Verify variable names are correct (case-sensitive)
- Make sure there are no extra spaces
- Restart the server after changing `.env`

### Issue: "Module not found" errors

**Solution:**
```bash
pip3 install -r requirements.txt
```

### Issue: "Port 8000 already in use"

**Solution:**
- Change PORT in `.env` to another number (e.g., 8001)
- Or kill the process using port 8000:
  ```bash
  lsof -ti:8000 | xargs kill
  ```

### Issue: "Invalid authentication credentials"

**Solution:**
- Logout and login again
- Check that your JWT_SECRET is set correctly
- Verify Supabase keys are correct

### Issue: "Error loading criteria"

**Solution:**
- Make sure you've run all database migrations
- Check Supabase Table Editor to verify columns exist
- Check browser console (F12) for specific errors

### Issue: Email monitoring not working

**Solution:**
- Verify app password is correct
- Check that 2-factor authentication is enabled
- Verify email provider is correct
- Check server logs for IMAP connection errors
- Try "Check Email Now" button to test manually

---

## Next Steps After Setup

1. **Test with real listings**: Try analyzing different Homegate listings
2. **Configure email monitoring**: Set up your email filters if you want automatic monitoring
3. **Customize criteria**: Update your profile with your actual apartment preferences
4. **Share with users**: Deploy to production (Render, Heroku, etc.)

---

## Production Deployment (Optional)

If you want to deploy to production:

1. **Push to GitHub**: Commit your code (but NOT `.env` file!)
2. **Deploy to Render**:
   - Connect your GitHub repo
   - Set environment variables in Render dashboard
   - Deploy!

3. **Update CORS_ORIGINS**: Add your production domain to `.env`

---

## Summary

**What you've accomplished:**
- ✅ Set up Supabase database with all tables
- ✅ Configured environment variables
- ✅ Installed all dependencies
- ✅ Started the application
- ✅ Created user account
- ✅ Configured profile and criteria
- ✅ Tested the application

**Time required:** ~30-45 minutes for complete setup

**You're now ready to use REPA!** 🎉

---

## Quick Reference Commands

```bash
# Start the server
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Install dependencies
pip3 install -r requirements.txt

# Check if server is running
curl http://localhost:8000

# View logs
# (Check terminal where server is running)
```

---

## Need Help?

If you get stuck:
1. Check the error message in terminal/server logs
2. Verify all environment variables are set correctly
3. Check that all database migrations ran successfully
4. Make sure Python version is 3.8+
5. Check browser console (F12) for frontend errors

Good luck! 🚀


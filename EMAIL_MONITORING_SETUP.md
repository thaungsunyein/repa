# Email Monitoring Setup Guide

REPA now supports automatic email monitoring! Configure which emails to monitor by setting custom sender filters and subject keywords. REPA will automatically extract listing URLs and analyze them against your criteria.

## Features

- ✅ Automatic email monitoring (checks every 5 minutes)
- ✅ **Configurable sender filter** - Set which email sender to monitor (e.g., "homegate", "immoscout24")
- ✅ **Configurable subject keywords** - Set which keywords must appear in the subject (e.g., "match", "new listing")
- ✅ Extracts listing URLs from emails
- ✅ Prevents duplicate processing
- ✅ Manual email check button
- ✅ Supports Gmail, Outlook, Yahoo, and iCloud

## Setup Steps

### 1. Update Database Schema

Run the SQL migrations in Supabase SQL Editor:

**First, run the basic email monitoring schema** (`supabase_schema_email.sql`):

```sql
-- Add email monitoring columns to user_criteria table
ALTER TABLE user_criteria 
ADD COLUMN IF NOT EXISTS monitor_email TEXT,
ADD COLUMN IF NOT EXISTS email_provider TEXT DEFAULT 'gmail',
ADD COLUMN IF NOT EXISTS email_app_password TEXT,
ADD COLUMN IF NOT EXISTS email_monitoring_enabled BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS last_email_check TIMESTAMP WITH TIME ZONE;

-- Create index for email monitoring queries
CREATE INDEX IF NOT EXISTS idx_user_criteria_email_monitoring 
ON user_criteria(user_id) 
WHERE email_monitoring_enabled = TRUE;

-- Create table to track processed emails (prevent duplicates)
CREATE TABLE IF NOT EXISTS processed_emails (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    email_message_id TEXT NOT NULL,
    email_subject TEXT,
    email_from TEXT,
    listing_url TEXT,
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    analysis_result JSONB,
    UNIQUE(user_id, email_message_id)
);

-- Create index for processed emails
CREATE INDEX IF NOT EXISTS idx_processed_emails_user_id 
ON processed_emails(user_id);

CREATE INDEX IF NOT EXISTS idx_processed_emails_message_id 
ON processed_emails(email_message_id);

-- Enable Row Level Security for processed_emails
ALTER TABLE processed_emails ENABLE ROW LEVEL SECURITY;

-- Create policy: Users can only see their own processed emails
CREATE POLICY "Users can view own processed emails"
    ON processed_emails FOR SELECT
    USING (auth.uid() = user_id);

-- Create policy: Users can insert their own processed emails
CREATE POLICY "Users can insert own processed emails"
    ON processed_emails FOR INSERT
    WITH CHECK (auth.uid() = user_id);
```

**Then, run the email filtering configuration schema** (`supabase_schema_email_filters.sql`):

```sql
-- Add configurable email filtering fields
ALTER TABLE user_criteria 
ADD COLUMN IF NOT EXISTS email_sender TEXT;

ALTER TABLE user_criteria 
ADD COLUMN IF NOT EXISTS email_subject_keywords TEXT;

COMMENT ON COLUMN user_criteria.email_sender IS 'Email sender/recipient to filter (e.g., "homegate", "immoscout24"). Leave empty to process all emails.';
COMMENT ON COLUMN user_criteria.email_subject_keywords IS 'Comma-separated keywords that must appear in email subject (e.g., "match,new listing"). At least one keyword must match.';

CREATE INDEX IF NOT EXISTS idx_user_criteria_email_sender 
ON user_criteria(email_sender) 
WHERE email_sender IS NOT NULL;
```

### 2. Install Dependencies

```bash
pip install beautifulsoup4
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

### 3. Configure Email Monitoring

1. Go to your Profile page (`/profile`)
2. Scroll down to the "Email Monitoring" section
3. Enable email monitoring by checking the checkbox
4. Enter your email address (the one that receives property listing notifications)
5. Select your email provider (Gmail, Outlook, Yahoo, or iCloud)
6. **Configure Email Sender Filter** (optional):
   - Enter the sender name to filter (e.g., "homegate", "immoscout24", "flatfox")
   - Leave empty to process emails from any sender
   - Default: "homegate" if not specified
7. **Configure Subject Keywords** (optional):
   - Enter comma-separated keywords that must appear in the subject
   - Examples: "match", "match,new listing", "alert,notification"
   - At least one keyword must match for the email to be processed
   - Default: "match" if not specified
8. Enter your app-specific password (see below for instructions)
9. Click "Save Criteria"

### 4. Get App-Specific Password

#### For Gmail:
1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Navigate to **Security** → **2-Step Verification**
3. Scroll down to **App passwords**
4. Generate a new app password for "Mail"
5. Copy the 16-character password and paste it into REPA

#### For Outlook/Office365:
1. Go to [Microsoft Account Security](https://account.microsoft.com/security)
2. Navigate to **Advanced security options**
3. Under **App passwords**, create a new app password
4. Copy the password and paste it into REPA

#### For Yahoo:
1. Go to [Yahoo Account Security](https://login.yahoo.com/account/security)
2. Navigate to **App passwords**
3. Generate a new app password
4. Copy and paste into REPA

#### For iCloud:
1. Go to [Apple ID Account](https://appleid.apple.com/)
2. Navigate to **Sign-In and Security** → **App-Specific Passwords**
3. Generate a new password
4. Copy and paste into REPA

## How It Works

1. **Automatic Monitoring**: REPA checks your email every 5 minutes for new messages
2. **Email Filtering**: 
   - Filters emails from the configured sender (or "homegate" by default)
   - Checks if the subject contains at least one of your configured keywords (or "match" by default)
   - Both filters must pass for the email to be processed
3. **URL Extraction**: Extracts listing URLs from the email body (HTML and plain text)
4. **Duplicate Prevention**: Tracks processed emails to avoid analyzing the same listing twice
5. **Automatic Analysis**: When a new listing is found, REPA automatically analyzes it against your criteria

## Configuration Examples

### Example 1: Default Homegate Setup
- **Email Sender**: `homegate` (or leave empty)
- **Subject Keywords**: `match` (or leave empty)
- **Result**: Processes emails from Homegate with "match" in subject

### Example 2: Multiple Keywords
- **Email Sender**: `homegate`
- **Subject Keywords**: `match,new listing,alert`
- **Result**: Processes emails from Homegate if subject contains "match" OR "new listing" OR "alert"

### Example 3: Different Sender
- **Email Sender**: `immoscout24`
- **Subject Keywords**: `match`
- **Result**: Processes emails from Immoscout24 with "match" in subject

### Example 4: All Senders, Specific Keywords
- **Email Sender**: (leave empty)
- **Subject Keywords**: `property,apartment,listing`
- **Result**: Processes emails from any sender if subject contains any of these keywords

## Manual Email Check

You can manually trigger an email check by clicking the "Check Email Now" button on your profile page. This is useful for testing or immediate checking.

## Security Notes

- App passwords are stored securely in the database
- App passwords are never returned in API responses
- Each user can only access their own email monitoring settings
- Row Level Security (RLS) ensures data isolation

## Troubleshooting

### Email check fails with authentication error
- Verify your app password is correct
- Make sure 2-factor authentication is enabled (required for app passwords)
- Check that your email provider is correctly selected

### No emails are being found
- Verify emails are arriving in your inbox
- Check that emails match your configured sender filter (or "homegate" by default)
- Check that emails contain at least one of your configured subject keywords (or "match" by default)
- Verify email monitoring is enabled in your profile
- Try using "Check Email Now" button to test immediately
- Check server logs for any error messages

### URLs not being extracted
- Homegate emails must contain URLs to homegate.ch, immoscout24.ch, or flatfox.ch
- Check that the email body contains clickable links (not just plain text URLs)

## API Endpoints

- `POST /api/user/check-email` - Manually trigger email check (requires authentication)
- `GET /api/user/criteria` - Get user criteria including email settings
- `POST /api/user/criteria` - Update criteria including email settings


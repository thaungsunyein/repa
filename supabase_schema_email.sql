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


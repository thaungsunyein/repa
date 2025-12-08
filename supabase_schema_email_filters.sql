-- Migration: Add configurable email filtering fields to user_criteria table
-- Run this in Supabase SQL Editor to add support for custom email sender and subject keyword filtering

-- Add email_sender column (for filtering by sender/recipient)
ALTER TABLE user_criteria 
ADD COLUMN IF NOT EXISTS email_sender TEXT;

-- Add email_subject_keywords column (comma-separated keywords for subject filtering)
ALTER TABLE user_criteria 
ADD COLUMN IF NOT EXISTS email_subject_keywords TEXT;

-- Add comments
COMMENT ON COLUMN user_criteria.email_sender IS 'Email sender/recipient to filter (e.g., "homegate", "immoscout24"). Leave empty to process all emails.';
COMMENT ON COLUMN user_criteria.email_subject_keywords IS 'Comma-separated keywords that must appear in email subject (e.g., "match,new listing"). At least one keyword must match.';

-- Create index for email sender filtering
CREATE INDEX IF NOT EXISTS idx_user_criteria_email_sender 
ON user_criteria(email_sender) 
WHERE email_sender IS NOT NULL;

-- Note: Default behavior if fields are NULL:
-- - email_sender = NULL: defaults to "homegate" in application code
-- - email_subject_keywords = NULL: defaults to "match" in application code


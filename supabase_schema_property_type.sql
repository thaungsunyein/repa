-- Migration: Add property_type column to user_criteria table
-- Run this in Supabase SQL Editor to add support for rent/buy selection

ALTER TABLE user_criteria 
ADD COLUMN IF NOT EXISTS property_type TEXT CHECK (property_type IN ('rent', 'buy') OR property_type IS NULL);

-- Add comment
COMMENT ON COLUMN user_criteria.property_type IS 'Property type: "rent" for rental, "buy" for purchase';

-- Create index for filtering by property type
CREATE INDEX IF NOT EXISTS idx_user_criteria_property_type 
ON user_criteria(property_type) 
WHERE property_type IS NOT NULL;


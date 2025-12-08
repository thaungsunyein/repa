# Database Migration Guide - Adding Property Type Field

This guide will help you add the `property_type` field to your `user_criteria` table in Supabase.

## Step-by-Step Instructions

### Step 1: Open Supabase Dashboard

1. Go to [https://supabase.com](https://supabase.com) and sign in
2. Select your REPA project from the dashboard

### Step 2: Open SQL Editor

1. In the left sidebar, click on **SQL Editor**
2. You'll see a list of saved queries (if any) and a query editor

### Step 3: Create New Query

1. Click the **"New query"** button (usually at the top right or in the query list)
2. A new query tab/editor will open

### Step 4: Copy the Migration SQL

Open the file `supabase_schema_property_type.sql` in your project and copy its entire contents:

```sql
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
```

### Step 5: Paste and Run

1. Paste the SQL code into the query editor
2. Review the SQL to make sure it looks correct
3. Click the **"Run"** button (or press `Ctrl+Enter` / `Cmd+Enter`)
4. Wait for the execution to complete (usually takes 1-2 seconds)

### Step 6: Verify Success

You should see a success message like:
- ✅ "Success. No rows returned"
- Or a message indicating the column/index was created

### Step 7: Verify in Table Editor

1. Go to **Table Editor** in the left sidebar
2. Click on the `user_criteria` table
3. You should now see a new column called `property_type` in the table schema
4. The column should be of type `TEXT` and allow NULL values

## Troubleshooting

### Error: "relation user_criteria does not exist"
- **Solution**: You need to run `supabase_schema.sql` first to create the base table
- Go back to Step 3 in SETUP.md and create the `user_criteria` table first

### Error: "column property_type already exists"
- **Solution**: This is fine! The migration uses `IF NOT EXISTS`, so it won't fail if the column already exists
- You can safely ignore this or skip the migration

### Error: "permission denied"
- **Solution**: Make sure you're logged in as the project owner or have admin permissions
- Check that you're in the correct Supabase project

## What This Migration Does

1. **Adds `property_type` column**: Allows storing "rent" or "buy" preference
2. **Adds CHECK constraint**: Ensures only valid values ('rent', 'buy') or NULL can be stored
3. **Adds index**: Improves query performance when filtering by property type
4. **Adds comment**: Documents what the column is for

## After Migration

Once the migration is complete:
- ✅ The `property_type` field will be available in the Profile form
- ✅ Users can select "Rent" or "Buy" when saving their criteria
- ✅ The AI will extract and use property type when analyzing listings
- ✅ Existing records will have `property_type = NULL` (which is fine)

## Need Help?

If you encounter any issues:
1. Check the Supabase logs in the **Logs** section
2. Verify your database connection
3. Make sure you're running the SQL in the correct project


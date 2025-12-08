# Database Migration Guide - Complete Setup

This guide will help you apply all database migrations to add the new features (property type and configurable email filters) to your Supabase database.

## Prerequisites

- ✅ You have a Supabase account and project set up
- ✅ You have access to your Supabase project dashboard
- ✅ The base `user_criteria` table already exists (from initial setup)

## Migration Files to Apply

You need to run **2 migration files** in order:

1. **`supabase_schema_property_type.sql`** - Adds property type (rent/buy) field
2. **`supabase_schema_email_filters.sql`** - Adds configurable email filtering fields

---

## Step-by-Step Instructions

### Step 1: Access Supabase Dashboard

1. Go to [https://supabase.com](https://supabase.com)
2. Sign in with your account
3. Select your **REPA project** from the dashboard

### Step 2: Open SQL Editor

1. In the left sidebar, click on **"SQL Editor"** (it has a database icon)
2. You'll see the SQL Editor interface with:
   - A list of saved queries (if any) on the left
   - A query editor in the center
   - A "New query" button

### Step 3: Create New Query for Property Type Migration

1. Click the **"New query"** button (usually at the top right)
2. A new query tab/editor will open
3. Give it a name like "Add Property Type Field" (optional but helpful)

### Step 4: Run Property Type Migration

1. Open the file `supabase_schema_property_type.sql` from your project
2. **Copy ALL the SQL code** from that file:

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

3. **Paste** the SQL into the query editor
4. **Review** the SQL to make sure it looks correct
5. Click the **"Run"** button (or press `Ctrl+Enter` / `Cmd+Enter`)
6. Wait for execution (usually 1-2 seconds)

**Expected Result:**
- ✅ Success message: "Success. No rows returned" or similar
- ✅ No error messages

### Step 5: Verify Property Type Migration

1. Go to **"Table Editor"** in the left sidebar
2. Click on the **`user_criteria`** table
3. You should see a new column called **`property_type`**
4. The column should be of type `TEXT` and allow NULL values

### Step 6: Create New Query for Email Filters Migration

1. Go back to **SQL Editor**
2. Click **"New query"** again
3. Name it "Add Email Filter Fields" (optional)

### Step 7: Run Email Filters Migration

1. Open the file `supabase_schema_email_filters.sql` from your project
2. **Copy ALL the SQL code** from that file:

```sql
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
```

3. **Paste** the SQL into the query editor
4. **Review** the SQL
5. Click **"Run"**
6. Wait for execution

**Expected Result:**
- ✅ Success message
- ✅ No error messages

### Step 8: Verify Email Filters Migration

1. Go back to **"Table Editor"**
2. Click on **`user_criteria`** table again
3. You should now see **two new columns**:
   - **`email_sender`** (TEXT, nullable)
   - **`email_subject_keywords`** (TEXT, nullable)

### Step 9: Final Verification

Your `user_criteria` table should now have these columns:

**Original columns:**
- id, user_id, location, min_rooms, max_rooms, etc.

**New columns added:**
- ✅ `property_type` (TEXT) - for rent/buy selection
- ✅ `email_sender` (TEXT) - for sender filtering
- ✅ `email_subject_keywords` (TEXT) - for subject keyword filtering

---

## Troubleshooting

### Error: "relation user_criteria does not exist"

**Problem:** The base table hasn't been created yet.

**Solution:**
1. First run `supabase_schema.sql` to create the base table
2. Then run the migrations above

### Error: "column property_type already exists"

**Problem:** The migration was already run.

**Solution:** 
- This is fine! The migrations use `IF NOT EXISTS`, so they're safe to run multiple times
- You can skip this migration or ignore the warning

### Error: "permission denied"

**Problem:** You don't have admin access to the database.

**Solution:**
- Make sure you're logged in as the project owner
- Check that you're in the correct Supabase project
- Contact your project administrator if needed

### Error: "syntax error" or SQL execution fails

**Problem:** The SQL might have been copied incorrectly.

**Solution:**
- Make sure you copied the ENTIRE SQL block (including all lines)
- Check for any extra characters or missing semicolons
- Try copying from the file again
- Make sure you're pasting into a new query, not modifying an existing one

### Can't see the new columns in Table Editor

**Solution:**
- Refresh the Table Editor page
- Make sure you're looking at the correct table (`user_criteria`)
- Check that the migrations ran successfully (look for success messages)
- Try clicking "Refresh" or reloading the page

---

## Quick Reference: All Migration Files

If you need to run all migrations from scratch, here's the order:

1. **`supabase_schema.sql`** - Creates base `user_criteria` table (if not done already)
2. **`supabase_schema_email.sql`** - Adds email monitoring fields (if not done already)
3. **`supabase_schema_property_type.sql`** - Adds property_type field ⬅️ **Run this**
4. **`supabase_schema_email_filters.sql`** - Adds email filter fields ⬅️ **Run this**

---

## After Migration

Once both migrations are complete:

✅ **Property Type Feature:**
- Users can select "Rent" or "Buy" in their Profile
- The AI will extract and use property type when analyzing listings
- Match reports will filter by property type

✅ **Email Filtering Feature:**
- Users can configure which email sender to monitor
- Users can configure which keywords must appear in subject
- Defaults to "homegate" sender and "match" keyword if not configured

---

## Need Help?

If you encounter issues:

1. **Check Supabase Logs:**
   - Go to **Logs** section in Supabase dashboard
   - Look for any error messages

2. **Verify Database Connection:**
   - Make sure your Supabase project is active
   - Check that you can access the Table Editor

3. **Test the Application:**
   - After migrations, test the Profile page
   - Try saving criteria with the new fields
   - Verify the fields appear and save correctly

4. **Rollback (if needed):**
   - If something goes wrong, you can manually drop columns:
   ```sql
   ALTER TABLE user_criteria DROP COLUMN IF EXISTS property_type;
   ALTER TABLE user_criteria DROP COLUMN IF EXISTS email_sender;
   ALTER TABLE user_criteria DROP COLUMN IF EXISTS email_subject_keywords;
   ```

---

## Summary

**What you're doing:**
- Adding 3 new columns to the `user_criteria` table
- Making email monitoring configurable
- Adding property type support

**Time required:** ~5 minutes

**Difficulty:** Easy (just copy-paste SQL)

**Risk:** Low (migrations use `IF NOT EXISTS`, safe to run multiple times)

Good luck! 🚀


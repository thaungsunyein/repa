# ⚡ Quick Start Checklist

Follow these steps in order to get REPA running:

## ✅ Step 1: Database Setup (5 minutes)

1. **Create Supabase Project**
   - Go to https://supabase.com → New Project
   - Wait for project creation (~2 minutes)

2. **Get Credentials**
   - Settings → API → Copy: URL, anon key, service_role key

3. **Run SQL Migrations** (in Supabase SQL Editor):
   - ✅ Run `supabase_schema.sql` → Creates base tables
   - ✅ Run `supabase_schema_email.sql` → Adds email monitoring tables
   - ✅ Run `supabase_schema_property_type.sql` → Adds property_type field
   - ✅ Run `supabase_schema_email_filters.sql` → Adds email filter fields

**Verify:** Table Editor → `user_criteria` table should have all columns

---

## ✅ Step 2: Environment Setup (5 minutes)

1. **Create `.env` file** in project root
2. **Copy from `.env.example`** and fill in:
   - OpenAI API key
   - Firecrawl API key
   - Supabase URL and keys

**Verify:** `.env` file exists with all values filled

---

## ✅ Step 3: Install Dependencies (2 minutes)

```bash
cd /Users/gildafernandezconchajahnsen/repa
pip3 install -r requirements.txt
```

**Verify:** No errors during installation

---

## ✅ Step 4: Start Server (1 minute)

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

**Verify:** 
- Server starts without errors
- Visit http://localhost:8000 → See login page

---

## ✅ Step 5: Create Account (1 minute)

1. Open http://localhost:8000
2. Click "Sign up"
3. Enter email and password
4. Click "Sign Up"

**Verify:** Logged in, see chat interface

---

## ✅ Step 6: Configure Profile (2 minutes)

1. Click "Profile" in header
2. Fill in apartment criteria:
   - Property Type: Rent/Buy
   - Location, rooms, rent, etc.
3. (Optional) Configure email monitoring
4. Click "Save Criteria"

**Verify:** "Criteria saved successfully!" message

---

## ✅ Step 7: Test (2 minutes)

1. Go to chat page
2. Send message with listing URL:
   ```
   Looking for 3 rooms in Zürich, max CHF 3000.
   Check: https://www.homegate.ch/rent/4002583790
   ```
3. Wait for analysis

**Verify:** See detailed match report

---

## 🎉 Done!

Total time: ~20 minutes

**If something fails:**
- Check `COMPLETE_SETUP_GUIDE.md` for detailed troubleshooting
- Check server logs in terminal
- Check browser console (F12)


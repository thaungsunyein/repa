# 🚀 Render Deployment Guide - Step by Step

## Prerequisites Checklist

Before starting, make sure you have:
- [x] GitHub account
- [x] Render account (just created ✅)
- [x] All API keys ready:
  - OpenAI API Key
  - Firecrawl API Key
  - Supabase URL, Anon Key, Service Role Key
- [x] Supabase database set up and migrations run

---

## Step 1: Push Code to GitHub

### If you haven't pushed to GitHub yet:

1. **Create a GitHub repository:**
   - Go to https://github.com/new
   - Name it: `repa` (or your preferred name)
   - Choose Public or Private
   - Don't initialize with README (you already have one)

2. **Push your code:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/repa.git
   git branch -M main
   git push -u origin main
   ```

### If you already have a GitHub repo:
```bash
git push origin main
```

---

## Step 2: Connect Render to GitHub

1. **Go to Render Dashboard:**
   - Visit https://dashboard.render.com
   - Sign in with your account

2. **Authorize GitHub:**
   - Click "New +" → "Web Service"
   - If prompted, authorize Render to access your GitHub
   - Select your GitHub account/organization

3. **Select Repository:**
   - Find and select your `repa` repository
   - Click "Connect"

---

## Step 3: Configure Web Service

Render should auto-detect settings from `render.yaml`, but verify:

### Basic Settings:
- **Name:** `repa` (or your choice)
- **Region:** Choose closest to your users (e.g., Frankfurt for Europe)
- **Branch:** `main`
- **Root Directory:** Leave empty (root)
- **Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app:app --host 0.0.0.0 --port $PORT`

### Plan:
- **Select:** "Free" (for testing)

---

## Step 4: Add Environment Variables

Click "Advanced" → "Add Environment Variable" and add these:

### Required Variables:

```
OPENAI_API_KEY=your_openai_api_key_here
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_KEY=your_supabase_service_role_key_here
```

### Optional Variables:

```
JWT_SECRET=your_jwt_secret_here
PORT=8000
CORS_ORIGINS=https://repa.onrender.com
```

**Important:** 
- Get these from your `.env` file (don't commit `.env`!)
- Copy values exactly (no quotes needed)
- Click "Add" after each variable

---

## Step 5: Deploy

1. **Click "Create Web Service"**
2. **Wait for deployment:**
   - First deploy takes ~5-10 minutes
   - Watch the build logs
   - You'll see: "Building...", "Deploying...", "Live"

3. **Get your URL:**
   - Once deployed, you'll see: `https://repa.onrender.com` (or similar)
   - Copy this URL!

---

## Step 6: Test Deployment

1. **Visit your URL:** `https://repa.onrender.com`
   - If first visit after 15 min: Wait ~1 minute for cold start
   - Should see login page

2. **Test Registration:**
   - Create a test account
   - Verify it works

3. **Test Chat:**
   - Send a test message with a listing URL
   - Verify analysis works

4. **Check Logs:**
   - In Render dashboard → "Logs" tab
   - Look for any errors

---

## Step 7: Update CORS (If Needed)

If you get CORS errors:

1. **In Render Dashboard:**
   - Go to your service → "Environment"
   - Add/update: `CORS_ORIGINS=https://repa.onrender.com`
   - Save changes (auto-redeploys)

2. **Or update in code:**
   - `app.py` already includes `https://repa.onrender.com` in CORS_ORIGINS
   - Should work automatically

---

## Troubleshooting

### Issue: Build Fails
**Check:**
- Requirements.txt is correct
- Python version (Render uses Python 3.11 by default)
- Build logs for specific errors

**Solution:**
- Check `requirements.txt` syntax
- Verify all dependencies are listed

### Issue: Service Won't Start
**Check:**
- Start command is correct: `uvicorn app:app --host 0.0.0.0 --port $PORT`
- Port uses `$PORT` variable (Render requirement)
- Logs tab for error messages

### Issue: Environment Variables Not Working
**Check:**
- Variables are set correctly (no quotes, no spaces)
- Names match exactly (case-sensitive)
- Clicked "Save Changes" after adding

### Issue: Database Connection Fails
**Check:**
- Supabase URL is correct
- Service role key is set (for backend operations)
- Database tables exist (run migrations)
- Supabase allows connections from Render IPs

### Issue: Cold Start Too Slow
**Normal:** First request after 15 min inactivity takes ~1 minute
**Solution:** 
- Accept it (free tier limitation)
- Or upgrade to $7/month for always-on

---

## Post-Deployment Checklist

- [ ] Service is running (green status)
- [ ] Can access URL in browser
- [ ] Registration works
- [ ] Login works
- [ ] Chat endpoint works
- [ ] Profile page loads
- [ ] Database operations work
- [ ] No errors in logs

---

## Share with Team

Once deployed, share:
- **URL:** `https://repa.onrender.com` (or your custom URL)
- **Note:** First request after inactivity may take ~1 minute
- **Testing Guide:** See `TESTING_GUIDE.md`

---

## Monitoring

### Check Service Status:
- Render Dashboard → Your Service → "Metrics"
- Monitor: CPU, Memory, Requests

### View Logs:
- Render Dashboard → Your Service → "Logs"
- Real-time logs for debugging

### Update Code:
- Push to `main` branch → Auto-deploys
- Or manually trigger: "Manual Deploy" → "Deploy latest commit"

---

## Cost Monitoring

**Free Tier Limits:**
- Instance Hours: 750/month (check in dashboard)
- Bandwidth: 100GB/month (check in dashboard)
- Build Minutes: 500/month

**If Approaching Limits:**
- Consider upgrading to Starter ($7/month)
- Or optimize usage

---

## Next Steps

1. ✅ Deploy to Render
2. ✅ Test all features
3. ✅ Share URL with team
4. ✅ Monitor usage
5. ✅ Consider upgrade if needed

---

**Need Help?** Check Render docs: https://render.com/docs

**Last Updated:** Version 2


# 🧪 REPA Testing Guide for Team

## Quick Testing Options

### Option 1: Test on Deployed Version (If Available)

If REPA is deployed to Render or another hosting service, share this link:

**🔗 Production URL:** `https://repa.onrender.com` (or your deployed URL)

**Note:** Check if the deployment is active. If not deployed yet, use Option 2.

---

### Option 2: Local Testing (Recommended for Development)

Each team member can run REPA locally on their machine.

#### Prerequisites
- Python 3.8+ installed
- Git installed
- API keys (OpenAI, Firecrawl, Supabase)

#### Quick Setup Steps

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd repa
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Copy `.env.example` to `.env` (if exists) OR create `.env` file
   - Add your API keys (see `SETUP.md` for details)

4. **Set up Supabase database:**
   - Create a Supabase project at [supabase.com](https://supabase.com)
   - Run `supabase_schema.sql` in Supabase SQL Editor
   - Run `supabase_schema_email.sql` (if using email monitoring)
   - Get your Supabase keys from Settings → API

5. **Run the server:**
   ```bash
   python3 app.py
   # OR
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```

6. **Access the app:**
   Open your browser: **http://localhost:8000**

---

## 🎯 Testing Checklist

### Basic Functionality Tests

#### ✅ 1. Authentication
- [ ] Register a new account
- [ ] Login with credentials
- [ ] Logout works
- [ ] Session persists after page refresh

#### ✅ 2. Chat Interface
- [ ] Send a message with apartment criteria
- [ ] Include a listing URL (e.g., `https://www.homegate.ch/rent/4002583790`)
- [ ] Receive AI analysis response
- [ ] Markdown renders correctly
- [ ] Images display in analysis

#### ✅ 3. Profile Page
- [ ] Access profile page (`/profile`)
- [ ] Save apartment criteria
- [ ] Load saved criteria
- [ ] Update criteria
- [ ] Clear form works

#### ✅ 4. Email Monitoring (Optional)
- [ ] Enable email monitoring in profile
- [ ] Configure email settings
- [ ] Test manual email check
- [ ] Verify email filtering works

---

## 📝 Test Scenarios

### Scenario 1: Basic Apartment Search

**Input:**
```
I'm looking for a 3-room apartment in Zürich, max CHF 3000/month, 
with parking and balcony.

Check this: https://www.homegate.ch/rent/4002583790
```

**Expected:**
- Criteria extracted correctly
- Listing analyzed
- Match score provided
- Detailed analysis with images

### Scenario 2: Property Type (Rent vs Buy)

**Input:**
```
I want to buy a 4-room apartment in Bern, around 100m²
```

**Expected:**
- Property type set to "buy"
- Criteria saved correctly
- Analysis distinguishes rent vs buy listings

### Scenario 3: Email Monitoring

**Steps:**
1. Set up email monitoring in profile
2. Send yourself a test email with Homegate listing URLs
3. Click "Check Email Now"
4. Verify listings are analyzed automatically

**Expected:**
- Email is checked
- URLs extracted from email
- Listings analyzed automatically
- Results appear in profile page

---

## 🐛 Common Issues & Solutions

### Issue: "Cannot connect to server"
**Solution:** 
- Check if server is running: `python3 app.py`
- Verify port 8000 is not in use
- Check firewall settings

### Issue: "Authentication failed"
**Solution:**
- Verify Supabase credentials in `.env`
- Check database tables are created
- Ensure RLS policies are set up

### Issue: "API key error"
**Solution:**
- Verify all API keys in `.env` file
- Check OpenAI API key is valid
- Verify Firecrawl API key is active

### Issue: "Email monitoring not working"
**Solution:**
- Verify app-specific password is correct
- Check email provider settings
- Ensure email filters match test email
- Check server logs for errors

---

## 🔗 Useful Links for Testing

- **Homegate Test Listing:** https://www.homegate.ch/rent/4002583790
- **Supabase Dashboard:** https://supabase.com/dashboard
- **OpenAI API Keys:** https://platform.openai.com/api-keys
- **Firecrawl Dashboard:** https://firecrawl.dev

---

## 📊 What to Report

When testing, report:
1. **What worked** ✅
2. **What didn't work** ❌
3. **Error messages** (copy exact text)
4. **Browser console errors** (F12 → Console tab)
5. **Server logs** (terminal output)
6. **Steps to reproduce** issues

---

## 🚀 Quick Start for Non-Technical Testers

If you have a deployed version:

1. **Share the link:** `https://repa.onrender.com` (or your URL)
2. **Provide test account credentials** (or let them register)
3. **Share example test message:**
   ```
   I'm looking for a 2-room apartment in Zürich, max CHF 2500/month.
   Check this: https://www.homegate.ch/rent/4002583790
   ```
4. **Ask them to:**
   - Register/login
   - Send the test message
   - Check if they get an analysis
   - Try the profile page

---

## 📞 Support

If you encounter issues:
1. Check `README.md` for setup instructions
2. Review `SETUP.md` for detailed configuration
3. Check `CHANGES.md` for recent updates
4. Contact the development team

---

**Last Updated:** Version 2


# 🔗 REPA Testing Link for Team

## Quick Answer: How to Test REPA

### Option 1: Deployed Version (If Available)

**🔗 Production URL:** `https://repa.onrender.com`

**Note:** This URL is configured in the code, but you need to verify if it's actually deployed:
- Check your Render dashboard: https://dashboard.render.com
- If not deployed, follow Option 2 below

---

### Option 2: Local Testing (Recommended)

Each team member runs REPA on their own machine:

**Local URL:** `http://localhost:8000`

**Setup Time:** ~20 minutes (see `QUICK_START.md`)

---

## 📧 What to Send Your Team

### Email Template:

```
Subject: REPA v2 - Testing Instructions

Hi Team,

REPA (Real Estate Personalized Assistant) Version 2 is ready for testing!

🔗 TESTING OPTIONS:

Option 1 - Deployed Version (if available):
https://repa.onrender.com

Option 2 - Local Testing (recommended):
1. Clone the repo: git clone <repository-url>
2. Follow QUICK_START.md (takes ~20 minutes)
3. Access: http://localhost:8000

📋 QUICK TEST:
1. Register/Login
2. Send this message:
   "I'm looking for a 3-room apartment in Zürich, max CHF 3000/month.
   Check this: https://www.homegate.ch/rent/4002583790"
3. Verify you get an AI analysis

📚 Full Testing Guide: See TESTING_GUIDE.md
📖 Setup Instructions: See QUICK_START.md

Questions? Let me know!

Best,
[Your Name]
```

---

## 🎯 Quick Test Scenarios

### Test 1: Basic Functionality
```
Message: "I need a 2-room apartment in Bern, max CHF 2000/month"
URL: https://www.homegate.ch/rent/4002583790
```

### Test 2: Property Type
```
Message: "I want to buy a 4-room apartment in Zürich, around 100m²"
```

### Test 3: Profile Management
- Go to Profile page
- Save criteria
- Verify it loads correctly

---

## ✅ Pre-Deployment Checklist

Before sharing the link, ensure:

- [ ] Server is running (if local)
- [ ] Database is set up (Supabase)
- [ ] API keys are configured
- [ ] Test account works (or let them register)
- [ ] At least one test listing URL works

---

## 🚨 If Deployed Version Doesn't Work

1. **Check Render Dashboard:**
   - Is the service running?
   - Are environment variables set?
   - Check logs for errors

2. **Common Issues:**
   - Service might be sleeping (free tier)
   - Environment variables missing
   - Database not accessible

3. **Fallback:**
   - Use local testing (Option 2)
   - Share `QUICK_START.md` with team

---

## 📱 Share This File

You can share `TESTING_GUIDE.md` with your team for comprehensive testing instructions.

---

**Last Updated:** Version 2


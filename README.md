# 🏠 REPA - Real Estate Personalized Assistant

An AI-powered web app for matching apartment listings with user criteria. Built as a demo for the LangFlow-based Real Estate Personalized Assistant workflow.

## Features

- 💬 **Chat Interface** - Simple, clean UI for natural conversation
- 🔍 **Smart Criteria Extraction** - AI extracts structured data from natural language
- 🕷️ **Web Scraping** - Automatically fetches listing details from URLs
- 🖼️ **Image Analysis** - Analyzes apartment photos using vision AI
- ✅ **Match Scoring** - Generates detailed match reports with recommendations
- 📧 **Email Monitoring** - Automatically monitors your inbox for new property listings and analyzes them (configurable filters for sender and subject keywords)
- 👤 **User Profiles** - Save your apartment criteria for quick access
- 🔐 **Authentication** - Secure user accounts with Supabase

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Supabase Database

1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Run the SQL schema from `supabase_schema.sql` in the Supabase SQL Editor
3. Run the email monitoring schema from `supabase_schema_email.sql` (if not already included)
4. Get your Supabase credentials from Settings → API

### 3. Set Up API Keys

Create a `.env` file in the project root and add:

```env
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Firecrawl API Key
FIRECRAWL_API_KEY=your_firecrawl_api_key_here

# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_KEY=your_supabase_service_role_key_here

# Optional
JWT_SECRET=your_jwt_secret_here
PORT=8000
CORS_ORIGINS=http://localhost:8000,https://your-domain.com  # Comma-separated list of allowed origins (optional)
```

Get your API keys:
- **OpenAI API Key**: Get from [platform.openai.com](https://platform.openai.com/api-keys)
- **Firecrawl API Key**: Get from [firecrawl.dev](https://firecrawl.dev)
- **Supabase Keys**: Get from your Supabase project Settings → API

### 4. Run the App

**Option 1: Using Python directly**
```bash
python3 app.py
```

**Option 2: Using uvicorn directly (recommended)**
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The app will start at [http://localhost:8000](http://localhost:8000)

**Note:** On macOS and Linux, use `python3` instead of `python`.

## Usage

### Option 1: Manual Listing Analysis

1. Open [http://localhost:8000](http://localhost:8000) in your browser
2. Register or login to create your account
3. Describe what you're looking for in an apartment
4. Include a listing URL from Homegate.ch or similar sites
5. Send your message and wait for the AI analysis!

**Example Input:**
```
I'm visiting Switzerland for ski season and want to hit the slopes! 
I got my wife and her family coming along, with our two sons. 
So it will be 6-7 people. We want to be right close to the ski action!

Check this listing: https://www.homegate.ch/rent/4002583790
```

### Option 2: Automatic Email Monitoring (Recommended)

1. **Set up your criteria** - Go to your Profile page and fill in your apartment preferences
2. **Configure email monitoring** - In the Profile page:
   - Enable "Email Monitoring"
   - Enter the email address where you receive Homegate notifications
   - Select your email provider (Gmail, Outlook, Yahoo, or iCloud)
   - Enter an app-specific password (see setup instructions below)
   - Click "Save Criteria"
3. **Let REPA work automatically** - REPA will check your email every 5 minutes for emails matching your configured filters (sender and subject keywords), extract listing URLs, and automatically analyze them against your saved criteria!

**Getting App-Specific Passwords:**
- **Gmail**: Google Account → Security → 2-Step Verification → App passwords
- **Outlook**: Microsoft Account → Security → Advanced security options → App passwords
- **Yahoo**: Yahoo Account Security → App passwords
- **iCloud**: Apple ID → Sign-In and Security → App-Specific Passwords

### What You'll Get

- **Match Score** - Percentage match with your criteria
- **Detailed Analysis** - What matches and what doesn't
- **Property Highlights** - Key features of the listing
- **Image Analysis** - AI-powered photo descriptions with actual images
- **Recommendation** - Should you pursue this listing?
- **Next Steps** - Actionable advice
- **Personalized Contact Message** - Ready-to-send message for good matches

## How It Works

### Manual Analysis Flow

1. **Parse Input** - Extracts user criteria and listing URL from chat message
2. **Extract Criteria** - Uses GPT-4o-mini to structure requirements into JSON
3. **Scrape Listing** - Firecrawl fetches the full listing content
4. **Analyze Images** - GPT-4o-mini Vision analyzes apartment photos (up to 3 images)
5. **Generate Report** - GPT-4o-mini creates a comprehensive match analysis

### Email Monitoring Flow

1. **Background Check** - REPA checks your email every 5 minutes (IMAP)
2. **Email Filtering** - Processes emails based on your configured:
   - **Sender filter**: Which email sender to monitor (e.g., "homegate", "immoscout24")
   - **Subject keywords**: Keywords that must appear in subject (e.g., "match", "new listing")
   - Defaults to "homegate" sender and "match" keyword if not configured
3. **URL Extraction** - Extracts listing URLs from email body (HTML and plain text)
4. **Duplicate Prevention** - Tracks processed emails to avoid re-analysis
5. **Automatic Analysis** - For each new listing, runs the same analysis flow as manual mode
6. **Results Storage** - Analysis results are stored for your review

## Project Structure

```
repa/
├── app.py                      # FastAPI backend server
├── static/
│   ├── index.html             # Frontend chat UI
│   └── profile.html           # User profile and criteria management
├── requirements.txt           # Python dependencies
├── .env                       # Your API keys (create this)
├── supabase_schema.sql                    # Database schema for user criteria
├── supabase_schema_email.sql              # Database schema for email monitoring
├── supabase_schema_property_type.sql      # Migration: Add property_type (rent/buy)
├── supabase_schema_email_filters.sql      # Migration: Add email filter fields
├── CHANGES.md                             # Detailed changelog
├── CONTRIBUTING.md                        # Contribution guidelines
├── REPA Iteration 1 v3.json   # Original LangFlow workflow
├── SETUP.md                   # Detailed setup instructions
├── EMAIL_MONITORING_SETUP.md  # Email monitoring setup guide
└── README.md                  # This file
```

## API Endpoints

### Public Endpoints
- `GET /` - Serves the chat interface
- `GET /profile` - Serves the user profile page

### Authentication Endpoints
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login user and get JWT token

### Protected Endpoints (require JWT token)
- `POST /api/chat` - Processes chat messages
  - Request: `{ "message": "your message with criteria and URL" }`
  - Response: `{ "response": "AI analysis", "status": "success" }`
- `GET /api/user/criteria` - Get user's saved criteria
- `POST /api/user/criteria` - Create/update user's criteria
- `PUT /api/user/criteria` - Update user's criteria
- `POST /api/user/check-email` - Manually trigger email check

## Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth + JWT tokens
- **AI**: OpenAI GPT-4o-mini (text) + GPT-4o-mini (vision)
- **Web Scraping**: Firecrawl API
- **Email Monitoring**: IMAP with BeautifulSoup for parsing
- **Environment**: python-dotenv

## Cost Considerations

- OpenAI API costs depend on usage (gpt-4o-mini is very affordable)
- Firecrawl offers a free tier for testing
- Image analysis is limited to 5 images per request for cost control

## Customization

You can adjust settings in `app.py`:

- `max_images` - Change number of images to analyze (default: 3)
- `model` - Switch between `gpt-4o` and `gpt-4o-mini`
- `temperature` - Adjust AI creativity (default: 0.1 for consistency)

## Email Monitoring Details

REPA's email monitoring feature:

- **Automatic Checks**: Runs every 5 minutes in the background
- **Configurable Filtering**: 
  - Set which email sender to monitor (e.g., "homegate", "immoscout24", "flatfox")
  - Set subject keywords that must appear (e.g., "match", "new listing", "alert")
  - Defaults to "homegate" sender and "match" keyword if not configured
- **URL Extraction**: Finds listing URLs in both HTML and plain text email bodies
- **Duplicate Prevention**: Tracks processed emails to avoid analyzing the same listing twice
- **Supported Providers**: Gmail, Outlook/Office365, Yahoo Mail, iCloud Mail
- **Security**: Uses app-specific passwords (not your regular password)

For detailed setup instructions, see [EMAIL_MONITORING_SETUP.md](EMAIL_MONITORING_SETUP.md)

## Development Notes

This is a **production-ready MVP** with:

- ✅ User authentication and JWT tokens
- ✅ User profiles and criteria storage
- ✅ Email monitoring with automatic analysis
- ✅ Row Level Security (RLS) for data protection
- ✅ Background tasks for email checking

For further enhancements:

- Add email notifications when matches are found
- Implement caching for scraped listings
- Add user activity logging
- Add rate limiting per user
- Add tests

## License

MIT - This is a student project for educational purposes.

## Credits

Built for Group Project Course - Real Estate Personalized Assistant
Based on LangFlow workflow architecture

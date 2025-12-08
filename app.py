"""
REPA - Real Estate Personalized Assistant
A minimal demo app for the LangFlow-based apartment matching workflow
"""

from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import os
import json
import requests
import re
import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from supabase import create_client, Client
from jose import JWTError, jwt
from datetime import datetime, timedelta
import asyncio
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="REPA - Real Estate Personalized Assistant")

# Enable CORS
# Note: When allow_credentials=True, browsers reject allow_origins=["*"] for security
# Since we use JWT tokens in Authorization headers, we need credentials enabled
# Frontend is served from same origin, so same-origin requests don't trigger CORS
# But we configure CORS for cross-origin scenarios (e.g., different ports in dev)
CORS_ORIGINS_ENV = os.getenv("CORS_ORIGINS", "")
if CORS_ORIGINS_ENV:
    # Use explicit origins from environment variable
    CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGINS_ENV.split(",") if origin.strip()]
else:
    # Default: Allow common development and production origins
    CORS_ORIGINS = [
        "http://localhost:8000",
        "http://localhost:3000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:3000",
        "https://repa.onrender.com",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,  # Required for JWT tokens in Authorization header
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # Service role key for admin operations

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
# Use service role key for admin operations (bypasses RLS)
if SUPABASE_SERVICE_KEY:
    supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    logger.info("Supabase admin client initialized with service role key")
else:
    supabase_admin: Client = supabase
    logger.warning("SUPABASE_SERVICE_KEY not set - admin operations will use anon key (may fail with RLS)")

# JWT settings
JWT_SECRET = os.getenv("JWT_SECRET", SUPABASE_KEY)  # Use Supabase key as JWT secret
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Validate JWT_SECRET is set
if not JWT_SECRET:
    raise ValueError("JWT_SECRET or SUPABASE_KEY must be set in environment variables")

logger.info(f"JWT configured with algorithm {JWT_ALGORITHM}, expiration {JWT_EXPIRATION_HOURS} hours")

# Security
security = HTTPBearer()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    status: str = "success"


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str


class UserCriteriaRequest(BaseModel):
    location: Optional[str] = None
    property_type: Optional[str] = None  # "rent" or "buy"
    min_rooms: Optional[int] = None
    max_rooms: Optional[int] = None
    min_living_space: Optional[float] = None
    max_living_space: Optional[float] = None
    min_rent: Optional[float] = None
    max_rent: Optional[float] = None
    occupants: Optional[int] = None
    duration: Optional[str] = None
    starting_when: Optional[str] = None
    user_additional_requirements: Optional[dict] = None
    monitor_email: Optional[str] = None
    email_provider: Optional[str] = None
    email_app_password: Optional[str] = None
    email_monitoring_enabled: Optional[bool] = None
    email_sender: Optional[str] = None  # Email sender/recipient to filter (e.g., "homegate", "immoscout24")
    email_subject_keywords: Optional[str] = None  # Comma-separated keywords that must be in subject (e.g., "match,new listing")


class UserCriteriaResponse(BaseModel):
    id: str
    user_id: str
    location: Optional[str] = None
    property_type: Optional[str] = None  # "rent" or "buy"
    min_rooms: Optional[int] = None
    max_rooms: Optional[int] = None
    min_living_space: Optional[float] = None
    max_living_space: Optional[float] = None
    min_rent: Optional[float] = None
    max_rent: Optional[float] = None
    occupants: Optional[int] = None
    duration: Optional[str] = None
    starting_when: Optional[str] = None
    user_additional_requirements: Optional[dict] = None
    monitor_email: Optional[str] = None
    email_provider: Optional[str] = None
    email_monitoring_enabled: Optional[bool] = None
    email_sender: Optional[str] = None  # Email sender/recipient to filter
    email_subject_keywords: Optional[str] = None  # Comma-separated keywords for subject filtering
    last_email_check: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# Authentication helpers
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and return user_id"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning("Token missing 'sub' claim")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials: missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )
        logger.debug(f"Token verified for user_id: {user_id}")
        return user_id
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired. Please login again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError as e:
        logger.error(f"JWT verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Unexpected error verifying token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def extract_url_from_message(message: str) -> tuple[str, str]:
    """Extract URL from message and return cleaned message and URL"""
    url_pattern = r'(https?://[^\s]+)'
    urls = re.findall(url_pattern, message)
    
    if urls:
        # Get the first URL
        url = urls[0]
        # Remove URL from message
        clean_message = re.sub(url_pattern, '', message).strip()
        return clean_message, url
    
    return message, ""


def call_firecrawl_scraper(url: str) -> dict:
    """Scrape the listing URL using Firecrawl API"""
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        raise ValueError("FIRECRAWL_API_KEY not found in environment")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": url,
        "formats": ["markdown", "html"]
    }
    
    try:
        response = requests.post(
            "https://api.firecrawl.dev/v1/scrape",
            json=payload,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        
        if result.get("success"):
            data = result.get("data", {})
            return {
                "content": data.get("markdown", data.get("html", "")),
                "url": url,
                "metadata": data.get("metadata", {}),
                "title": data.get("metadata", {}).get("title", ""),
                "description": data.get("metadata", {}).get("description", ""),
            }
        else:
            return {"error": result.get("error", "Unknown error")}
    
    except Exception as e:
        return {"error": str(e)}


def extract_criteria_with_openai(user_message: str) -> dict:
    """Extract apartment criteria from user message using OpenAI"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment")
    
    system_prompt = """You are an expert at extracting structured apartment rental/purchase criteria from natural language.

Extract information from the user's request and return it as valid JSON.

IMPORTANT: Only include fields that the user explicitly mentions. Do NOT include fields with null values.

Available field names you may use (only if mentioned):
- property_type: "rent" or "buy" (string) - Extract if user mentions "rent", "rental", "lease", "buy", "purchase", "for sale", "to buy"
- location: The city, postal code, area, or proximity requirement (string)
- min_rooms: Minimum number of rooms (number)
- max_rooms: Maximum number of rooms (number)
- min_living_space: Minimum living space in square meters (number)
- max_living_space: Maximum living space in square meters (number)
- min_rent: Minimum rent in CHF (number) - only for rentals
- max_rent: Maximum rent in CHF (number) - only for rentals
- occupants: Number of people who will live there (number)
- duration: How long they need it (string, e.g., "ski season", "6 months", "long-term") - typically for rentals

For ANY other requirements (pet-friendly, balcony, parking, proximity to amenities, etc.), add them to an "additional_requirements" array.

Extraction Rules:
1. If user says "rent", "rental", "lease", "to rent" → use "property_type": "rent"
2. If user says "buy", "purchase", "for sale", "to buy" → use "property_type": "buy"
3. If not specified, default to "rent" (most common)
4. If "for X persons/people" → use "occupants": X
5. If "ski season" or temporary → use "duration": "ski season" or appropriate period
6. If "price is not a problem" or "budget flexible" → do NOT include min_rent or max_rent
7. If "more than X rooms" → use "min_rooms": X
8. If "less than CHF Y" → use "max_rent": Y (for rent) or note as price range (for buy)
9. If "about X square meters" → use both "min_living_space" and "max_living_space" with ±10% range
10. Location can be specific (city/postal code) OR proximity-based ("close to ski", "near train station")
11. Extract EACH specific requirement as a separate item in additional_requirements
12. Preserve the user's exact wording and intent
13. Infer room requirements from occupancy if helpful (e.g., 5 persons might suggest larger apartment)
14. Return ONLY valid JSON, no explanations

Example 1 - Rental with full numeric criteria:
Input: "I am looking to rent an apartment in 8008 Zürich, more than 4 rooms, living space about 100 square meters, and rent less than CHF 5000."
Output:
{
  "property_type": "rent",
  "location": "8008 Zürich",
  "min_rooms": 4,
  "min_living_space": 90,
  "max_living_space": 110,
  "max_rent": 5000
}

Example 2 - Purchase:
Input: "I want to buy an apartment in Zürich, 3-4 rooms, around 100m²"
Output:
{
  "property_type": "buy",
  "location": "Zürich",
  "min_rooms": 3,
  "max_rooms": 4,
  "min_living_space": 90,
  "max_living_space": 110
}

Example 3 - Seasonal rental:
Input: "I'm visiting Switzerland for a ski season and need to rent an apartment for 5 persons, need it to be super close to the ski action. Price is not a problem."
Output:
{
  "property_type": "rent",
  "occupants": 5,
  "duration": "ski season",
  "location": "ski resort area",
  "additional_requirements": ["close to ski slopes", "ski-in/ski-out preferred", "suitable for 5 people"]
}

Example 4 - Rental with mixed criteria:
Input: "Looking to rent 3 rooms in Zürich, max CHF 3000, with parking space, balcony, and modern kitchen"
Output:
{
  "property_type": "rent",
  "location": "Zürich",
  "min_rooms": 3,
  "max_rent": 3000,
  "additional_requirements": ["parking space", "balcony", "modern kitchen"]
}

Example 5 - Only location (defaults to rent):
Input: "I need an apartment in Bern"
Output:
{
  "property_type": "rent",
  "location": "Bern"
}

Now extract the criteria:"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    user_prompt = f"""Now extract the criteria from the User's Request:
<user_request>
{user_message}
</user_request>"""
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.1
    }
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        
        criteria_text = result['choices'][0]['message']['content']
        # Try to parse as JSON
        try:
            criteria = json.loads(criteria_text)
            return criteria
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            json_match = re.search(r'```json\s*(.*?)\s*```', criteria_text, re.DOTALL)
            if json_match:
                criteria = json.loads(json_match.group(1))
                return criteria
            return {"error": "Failed to parse criteria as JSON"}
    
    except Exception as e:
        return {"error": str(e)}


def analyze_images(listing_content: str, max_images: int = 5) -> str:
    """Analyze listing images using OpenAI Vision API"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "Image analysis skipped (no API key)"
    
    # Extract image URLs from markdown - support multiple image formats
    pattern = r'!\[.*?\]\((https://[^\)]+\.(?:jpg|jpeg|png|webp))\)'
    urls = re.findall(pattern, listing_content, re.IGNORECASE)
    
    # If no markdown images found, try to extract raw image URLs
    if not urls:
        pattern_raw = r'https://[^\s<>"]+\.(?:jpg|jpeg|png|webp)'
        urls = re.findall(pattern_raw, listing_content, re.IGNORECASE)
    
    if not urls:
        return "No images found to analyze"
    
    # Limit images
    urls = list(set(urls))[:max_images]
    
    print(f"[Image Analysis] Found {len(urls)} unique images to analyze")
    
    analyses = []
    for idx, url in enumerate(urls):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Analyze this apartment/property image. Identify:
1. Room type (living room, bedroom, kitchen, bathroom, exterior, view, etc.)
2. Key features and condition (modern, renovated, spacious, natural light, etc.)
3. Furnishing status (furnished, unfurnished, partially furnished)
4. Notable amenities or highlights
5. Overall impression (scale 1-10)

Be concise but specific. Focus on details that would matter to a renter."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": url,
                                "detail": "low"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            analysis = result['choices'][0]['message']['content']
            # IMPORTANT: Include the URL so the LLM can extract it and display the image
            analyses.append(f"### Image {idx + 1}\n**Image URL:** {url}\n\n{analysis}\n\n---\n\n")
        except Exception as e:
            analyses.append(f"### Image {idx + 1}\n**Image URL:** {url}\n❌ Analysis failed: {str(e)}\n\n---\n\n")
    
    summary = "\n".join(analyses)
    print(f"[Image Analysis] Completed. Sample output: {summary[:300]}...")
    return summary


def generate_match_report(criteria: dict, listing_data: dict, image_analysis: str = "") -> str:
    """Generate the final match report using OpenAI"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment")
    
    # Debug: Check what we're receiving
    print(f"[Debug generate_match_report] image_analysis length: {len(image_analysis) if image_analysis else 0}")
    print(f"[Debug generate_match_report] Has valid image analysis: {bool(image_analysis and image_analysis not in ['No images found to analyze', 'Image analysis skipped (no API key)'])}")
    
    system_prompt = """You are a helpful apartment rental/purchase advisor for the Swiss market. Your job is to analyze apartment listings and help users determine if they're a good match for their needs.

## Your Approach:
- Be friendly, conversational, and encouraging
- Extract all relevant details accurately from listings
- Compare listings objectively against the user's specific criteria
- **CRITICAL:** If user specified property_type (rent/buy), ONLY recommend listings that match. If listing is for rent but user wants to buy (or vice versa), mark as NOT A GOOD FIT immediately.
- Only evaluate criteria the user explicitly mentioned - don't penalize for unspecified requirements
- Be realistic about "close enough" matches (e.g., 95m² ≈ 100m², Zürich City ≈ 8008 Zürich)
- Distinguish between deal-breakers and nice-to-haves
- Provide honest, actionable recommendations

## Swiss Rental/Purchase Context:
- Understand Swiss room counting (e.g., 3.5 rooms = 2 bedrooms + living room + half room)
- Know typical Zürich pricing and neighborhoods (rental prices vs purchase prices)
- Recognize common Swiss rental/purchase terms and amenities
- Consider public transport accessibility and local area quality
- Rental listings show monthly rent (CHF/month), purchase listings show total price (CHF)

## Tone:
- Professional yet warm
- Clear and direct
- Helpful and supportive
- Honest about both positives and concerns

Follow the exact output format provided in the user's request."""

    # Determine if we have images to display
    has_images = image_analysis and image_analysis not in ["No images found to analyze", "Image analysis skipped (no API key)"]
    
    image_analysis_section = ""
    if has_images:
        image_analysis_section = f"""## Image Analysis Results:
{image_analysis}
"""
    
    image_gallery_section = ""
    if has_images:
        image_gallery_section = """## 📸 Photo Analysis

**INSTRUCTION:** Extract all image URLs from the Image Analysis section and create a beautiful photo gallery here. For each analyzed image:
1. Display the image using: ![Room Name](image_url)
2. Add a brief caption based on the analysis

Example format:
### Living Room
![Living Room](https://media2.homegate.ch/.../image1.jpg)
*Modern, spacious living area with natural light and contemporary furnishing.*

### Kitchen
![Kitchen](https://media2.homegate.ch/.../image2.jpg)
*Fully equipped kitchen with modern appliances and ample counter space.*

Continue for all analyzed images..."""
    
    with_images = " with photo gallery" if has_images else ""

    # Build the user prompt
    property_type_note = ""
    if criteria.get('property_type'):
        property_type_note = f"\n**IMPORTANT:** User is looking to {criteria.get('property_type')} (not {'buy' if criteria.get('property_type') == 'rent' else 'rent'}). Only recommend listings that match this property type."
    
    prompt = f"""User's criteria:
```json
{json.dumps(criteria, indent=2)}
```
{property_type_note}

Listing data:
<listing>
{listing_data.get('content', '')}
</listing>

{image_analysis_section}

---

## Your Task:

Analyze this apartment listing and create a beautiful, user-friendly match report{with_images}.

**CRITICAL IMAGE INSTRUCTION:** 
The listing data contains a **LISTING_IMAGE_URL:** field. You MUST extract the COMPLETE URL (do not truncate it) and insert it at the very top of your response using this EXACT format:
![Apartment](COMPLETE_URL_HERE)

Make sure to copy the entire URL exactly as provided, including all characters after the last slash.

### Output Format (use emojis and clear formatting):

```
# 🏠 Apartment Match Analysis

![Apartment](INSERT_COMPLETE_LISTING_IMAGE_URL_HERE)

## 📋 Listing Summary
**Title:** [listing title]
**Location:** [full address/area]
**Type:** [Rent/Buy - indicate if listing is for rent or purchase]
**Price:** CHF [amount]/month [for rent] or CHF [amount] [for purchase]
**Rooms:** [number] rooms
**Living Space:** [size] m²
**Available:** [date or immediately]

---

## 🎯 Match Score: [X]% 

[One sentence overall assessment]

---

## ✅ What Matches Your Criteria

[For EACH criterion that matches, use this format:]
**✓ [Criterion Name]**
• Your requirement: [what user asked for]
• Listing offers: [what listing has]
• Assessment: [brief positive note]

---

## ⚠️ Points to Consider

[For EACH criterion that doesn't match or is unclear:]
**⚠ [Criterion Name]**
• Your requirement: [what user asked for]
• Listing offers: [what listing has]
• Impact: [why this matters - deal-breaker or negotiable?]

[If no concerns: *No significant concerns - all criteria met!*]

---

## 💡 Key Highlights

• [Standout feature 1]
• [Standout feature 2]
• [Standout feature 3]
• [Other notable amenities]

---

{image_gallery_section}

---

## 🤔 Our Recommendation

**[HIGHLY RECOMMENDED / WORTH CONSIDERING / NOT A GOOD FIT]**

[2-3 sentences explaining why, considering the user's priorities and the listing's strengths/weaknesses. Be honest and helpful.]

---

## 📌 Next Steps

[If recommended: Suggest they contact the landlord, schedule viewing, etc.]
[If not recommended: Suggest what to look for instead]

---

[ONLY IF HIGHLY RECOMMENDED OR WORTH CONSIDERING:]

## ✉️ Personalized Contact Message

Ready to send! Copy this message for the "Contact Advertiser" form on the property website:

---
**Subject:** Interest in [Room count]-Room Apartment at [Location]

Dear Sir/Madam,

I am writing to express my strong interest in the [room count]-room apartment at [address/location] listed for CHF [price]/month.

[Include 2-3 sentences about why this apartment is perfect for them based on their criteria - be specific! Reference actual matches like "The 105m² living space and location in 8008 Zürich are exactly what I've been searching for."]

About me:
• [Infer likely tenant profile based on their search - e.g., "Professional working in Zürich" or "Small family" based on room requirements]
• Reliable, non-smoking tenant with excellent references
• Available to move in [reference availability date from listing or say "immediately"]
• Long-term rental desired

I am very interested in scheduling a viewing at your earliest convenience. I am flexible with timing and can meet this week if possible.

I have prepared all necessary documents (employment contract, salary statements, references) and am ready to proceed quickly given the competitive Zürich rental market.

Looking forward to hearing from you.

Best regards,
[Your Name]
[Your Phone]
[Your Email]
---

**Tip:** Personalize further by adding:
- Your current situation (relocating, growing family, etc.)
- Why you chose this specific listing
- Your move-in timeline
- Any relevant lifestyle details (quiet, respectful neighbor, etc.)

Good apartments in Zürich get many applications - send this today! ⚡
```

### Important Instructions:
1. **Be conversational and friendly** - write like you're helping a friend
2. **Use emojis** to make it visually appealing and scannable
3. **Be honest** - if something doesn't match, say so clearly
4. **Prioritize** - focus on what matters most (deal-breakers vs nice-to-haves)
5. **Only compare specified criteria** - don't penalize for unspecified requirements
6. **Extract all listing details** - even if not in criteria (they're useful to see)
7. **Be realistic** - 95m² is close enough to 100m², Zürich City ≈ 8008 Zürich
8. **Consider Swiss context** - room counting, pricing norms, etc.
9. **Make it actionable** - give clear next steps
10. **Generate contact message ONLY for recommended listings** - skip this section if "NOT A GOOD FIT"
11. **Personalize the contact message** based on the user's actual criteria matches (be specific about what matched!)
12. **Make the contact message professional yet warm** - increase their chances in competitive market

Return ONLY the formatted match analysis, ready to display to the user."""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }
    
    # Debug: Print the prompt being sent (first 1000 chars)
    print(f"[Debug] Prompt being sent to LLM (first 1000 chars):\n{prompt[:1000]}")
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        
        return result['choices'][0]['message']['content']
    
    except Exception as e:
        return f"Error generating match report: {str(e)}"


# Authentication endpoints
@app.post("/auth/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """Register a new user"""
    try:
        # Create user in Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password
        })
        
        if auth_response.user is None:
            raise HTTPException(status_code=400, detail="Registration failed")
        
        user_id = auth_response.user.id
        email = auth_response.user.email
        
        # Create access token
        access_token = create_access_token(data={"sub": user_id, "email": email})
        
        return AuthResponse(
            access_token=access_token,
            user_id=user_id,
            email=email
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Registration failed: {str(e)}")


@app.post("/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Login user and return JWT token"""
    try:
        # Authenticate with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if auth_response.user is None:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        user_id = auth_response.user.id
        email = auth_response.user.email
        
        # Create access token
        access_token = create_access_token(data={"sub": user_id, "email": email})
        
        return AuthResponse(
            access_token=access_token,
            user_id=user_id,
            email=email
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Login failed: {str(e)}")


# User Criteria endpoints
@app.get("/api/user/criteria", response_model=UserCriteriaResponse)
async def get_user_criteria(user_id: str = Depends(verify_token)):
    """Get user's saved criteria"""
    try:
        logger.info(f"Fetching criteria for user_id: {user_id}")
        # Use service role client for backend operations (bypasses RLS since we verify JWT ourselves)
        response = supabase_admin.table("user_criteria").select("*").eq("user_id", user_id).execute()
        
        if response.data and len(response.data) > 0:
            criteria_data = response.data[0]
            logger.info(f"Found criteria for user_id: {user_id}, data keys: {list(criteria_data.keys())}")
            logger.debug(f"Criteria data: {criteria_data}")
            # Remove app_password from response for security
            criteria_data.pop('email_app_password', None)
            return UserCriteriaResponse(**criteria_data)
        else:
            logger.info(f"No criteria found for user_id: {user_id}")
            raise HTTPException(status_code=404, detail="No criteria found for user")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching criteria for user_id {user_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching criteria: {str(e)}")


# Email Monitoring Functions
def get_imap_server(email_provider: str) -> str:
    """Get IMAP server address based on email provider"""
    providers = {
        'gmail': 'imap.gmail.com',
        'outlook': 'outlook.office365.com',
        'yahoo': 'imap.mail.yahoo.com',
        'icloud': 'imap.mail.me.com'
    }
    return providers.get(email_provider.lower(), 'imap.gmail.com')


def extract_urls_from_email_body(body: str) -> List[str]:
    """Extract URLs from email body (HTML or plain text)"""
    urls = []
    
    # Try parsing as HTML first
    try:
        soup = BeautifulSoup(body, 'html.parser')
        # Find all links
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href and ('homegate.ch' in href.lower() or 'immoscout24.ch' in href.lower() or 'flatfox.ch' in href.lower()):
                urls.append(href)
    except Exception as e:
        logging.debug(f"HTML parsing failed: {str(e)}")
    
    # Also search for URLs in plain text (more flexible pattern)
    # Match URLs from property websites - handle URLs on separate lines
    # Pattern matches URLs that may be on their own line or separated by whitespace
    # Updated pattern to handle URLs that might be on separate lines with newlines
    url_pattern = r'https?://[^\s<>"]*(?:homegate\.ch|immoscout24\.ch|flatfox\.ch)[^\s<>"]*'
    found_urls = re.findall(url_pattern, body, re.IGNORECASE)
    urls.extend(found_urls)
    
    # Handle URLs on separate lines (common in plain text emails)
    # Split by lines and check each line for URLs
    lines = body.split('\n')
    for line in lines:
        line = line.strip()
        # Check if line contains a URL (not just starts with http, might have whitespace)
        if 'http' in line.lower():
            # Check if it's a property URL
            if any(domain in line.lower() for domain in ['homegate.ch', 'immoscout24.ch', 'flatfox.ch']):
                # Extract the full URL (might have leading/trailing whitespace or characters)
                url_match = re.search(r'(https?://[^\s<>"]*(?:homegate\.ch|immoscout24\.ch|flatfox\.ch)[^\s<>"]*)', line, re.IGNORECASE)
                if url_match:
                    extracted_url = url_match.group(1).strip()
                    urls.append(extracted_url)
                    logging.debug(f"Found URL on line: {extracted_url}")
    
    # Also try a multiline pattern for URLs that might span or be separated
    simple_pattern = r'https?://[^\s\n<>"]*(?:homegate\.ch|immoscout24\.ch|flatfox\.ch)[^\s\n<>"]*'
    simple_urls = re.findall(simple_pattern, body, re.IGNORECASE | re.MULTILINE)
    urls.extend(simple_urls)
    
    # Remove duplicates and clean URLs
    unique_urls = []
    seen = set()
    for url in urls:
        url = url.strip().rstrip('/')  # Remove trailing slash
        if url and url not in seen:
            # Validate it's a proper URL
            if url.startswith('http://') or url.startswith('https://'):
                unique_urls.append(url)
                seen.add(url)
    
    logging.info(f"Extracted {len(unique_urls)} unique URLs from email: {unique_urls}")
    if len(unique_urls) == 0:
        logging.warning(f"No URLs extracted. Email body length: {len(body)} chars")
        logging.debug(f"Email body preview (first 1000 chars): {body[:1000]}")
    return unique_urls


def check_email_for_listings(
    email_address: str,
    app_password: str,
    email_provider: str,
    user_id: str,
    email_sender: Optional[str] = None,
    email_subject_keywords: Optional[str] = None
) -> List[dict]:
    """Check email inbox for new emails matching configured filters"""
    try:
        # Connect to IMAP server
        imap_server = get_imap_server(email_provider)
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_address, app_password)
        mail.select('INBOX')
        
        # Default values if not configured
        sender_filter = email_sender.lower().strip() if email_sender else None
        subject_keywords = [kw.strip().lower() for kw in email_subject_keywords.split(',')] if email_subject_keywords else ['match']
        
        # Handle multiple sender filters (comma-separated) - use OR logic
        # IMAP doesn't support OR directly, so we'll search all unread and filter in code
        search_criteria = ['UNSEEN']
        sender_filters_list = []
        if sender_filter:
            # Split by comma if multiple senders provided
            sender_filters_list = [s.strip() for s in sender_filter.split(',') if s.strip()]
            logging.info(f"Sender filters configured: {sender_filters_list}")
            # Note: IMAP FROM search only supports one sender at a time
            # We'll search all UNSEEN emails and filter by sender in code
            logging.info("Searching all unread emails, will filter by sender in code")
        else:
            logging.info("No sender filter configured, searching all unread emails")
        
        # Search for unread emails (we'll filter by sender and subject in code)
        # Note: We search all UNSEEN emails because IMAP doesn't support OR for multiple senders
        status, messages = mail.search(None, *search_criteria)
        
        if status != 'OK':
            mail.close()
            mail.logout()
            return []
        
        email_ids = messages[0].split()
        new_listings = []
        
        for email_id in email_ids:
            try:
                # Fetch email
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                if status != 'OK':
                    continue
                
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)
                
                # Get subject
                subject_header = email_message['Subject']
                if subject_header:
                    subject_decoded = decode_header(subject_header)
                    subject = subject_decoded[0][0] if subject_decoded else ''
                    if isinstance(subject, bytes):
                        subject = subject.decode('utf-8', errors='ignore')
                    else:
                        subject = str(subject) if subject else ''
                else:
                    subject = ''
                
                # Get sender email address for filtering
                sender_address = email_message['From'] or ''
                sender_lower = sender_address.lower()
                
                # Filter by sender if configured (check if any sender filter matches)
                if sender_filters_list:
                    sender_matches = False
                    for filter_sender in sender_filters_list:
                        # Check if filter matches sender email or domain
                        # e.g., "homegate" matches "noreply@homegate.ch" or "homegate.ch"
                        # e.g., "gilda.fernandezconcha@gmail.com" matches exact email
                        if filter_sender in sender_lower:
                            sender_matches = True
                            logging.debug(f"Sender filter '{filter_sender}' matches '{sender_address}'")
                            break
                    
                    if not sender_matches:
                        logging.debug(f"Skipping email - sender '{sender_address}' doesn't match any filter: {sender_filters_list}")
                        continue
                
                # Filter: only process emails with configured keywords in subject (case-insensitive)
                subject_lower = subject.lower()
                if not any(keyword in subject_lower for keyword in subject_keywords):
                    logging.debug(f"Skipping email - subject '{subject}' doesn't contain any of the keywords: {subject_keywords}")
                    continue
                
                logging.info(f"Processing email: Subject='{subject}', From='{sender_address}'")
                
                # Get message ID
                message_id = email_message['Message-ID'] or f"{email_id.decode()}"
                
                # Check if already processed (by message_id)
                processed = supabase_admin.table("processed_emails").select("*").eq("user_id", user_id).eq("email_message_id", message_id).execute()
                if processed.data and len(processed.data) > 0:
                    logging.info(f"Email '{subject}' (message_id: {message_id}) already processed, skipping")
                    continue
                
                # Extract body - prioritize plain text, fallback to HTML
                body = ""
                plain_text_body = ""
                html_body = ""
                
                if email_message.is_multipart():
                    for part in email_message.walk():
                        content_type = part.get_content_type()
                        if content_type == "text/plain":
                            try:
                                payload = part.get_payload(decode=True)
                                if payload:
                                    plain_text_body += payload.decode('utf-8', errors='ignore')
                            except Exception as e:
                                logging.debug(f"Error decoding plain text part: {e}")
                        elif content_type == "text/html":
                            try:
                                payload = part.get_payload(decode=True)
                                if payload:
                                    html_body += payload.decode('utf-8', errors='ignore')
                            except Exception as e:
                                logging.debug(f"Error decoding HTML part: {e}")
                else:
                    try:
                        body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        body = str(email_message.get_payload())
                
                # Use plain text if available, otherwise HTML
                if plain_text_body:
                    body = plain_text_body
                    logging.debug(f"Using plain text body (length: {len(body)} chars)")
                elif html_body:
                    body = html_body
                    logging.debug(f"Using HTML body (length: {len(body)} chars)")
                elif body:
                    logging.debug(f"Using single-part body (length: {len(body)} chars)")
                
                # Extract URLs
                logging.info(f"Extracting URLs from email body (length: {len(body)} chars)")
                # Log email body for debugging (first 2000 chars)
                logging.info(f"Email body preview (first 2000 chars):\n{body[:2000]}")
                urls = extract_urls_from_email_body(body)
                logging.info(f"✓ Found {len(urls)} URLs in email '{subject}': {urls}")
                
                # If fewer URLs than expected, log warning
                if len(urls) == 0:
                    logging.error(f"✗ No URLs extracted from email '{subject}'. Full body:\n{body}")
                elif len(urls) < 3:
                    logging.warning(f"⚠ Only {len(urls)} URL(s) extracted, might be missing some. Full body:\n{body}")
                
                # Log email body snippet for debugging if URLs seem incomplete
                if len(urls) > 0 and len(urls) < 3:
                    logging.warning(f"⚠ Only {len(urls)} URL(s) found, expected more. Email body preview (first 2000 chars):\n{body[:2000]}")
                elif not urls:
                    logging.warning(f"⚠ No URLs found in email '{subject}'. Email body preview (first 2000 chars):\n{body[:2000]}")
                
                # Log email body snippet for debugging (first 500 chars)
                if not urls:
                    logging.warning(f"No URLs found. Email body preview (first 500 chars): {body[:500]}")
                
                if urls:
                    new_listings.append({
                        'message_id': message_id,
                        'subject': subject,
                        'from': email_message['From'],
                        'urls': urls,
                        'received_date': email_message['Date']
                    })
                else:
                    logging.warning(f"No property URLs found in email. Email body length: {len(body)}")
                    
            except Exception as e:
                logging.error(f"Error processing email {email_id}: {str(e)}")
                continue
        
        mail.close()
        mail.logout()
        return new_listings
        
    except Exception as e:
        logging.error(f"Error checking email: {str(e)}")
        return []


async def process_new_email_listings(user_id: str, email_address: str, app_password: str, email_provider: str, email_sender: Optional[str] = None, email_subject_keywords: Optional[str] = None):
    """Process new email listings and trigger analysis"""
    try:
        logging.info(f"Starting email check for user {user_id}")
        logging.info(f"Filters - Sender: {email_sender}, Subject keywords: {email_subject_keywords}")
        
        # Check for new emails with configured filters
        new_listings = check_email_for_listings(email_address, app_password, email_provider, user_id, email_sender, email_subject_keywords)
        
        logging.info(f"Found {len(new_listings)} new listings to process")
        
        if not new_listings:
            logging.info("No new listings found")
            return
        
        # Get user criteria
        criteria_response = supabase_admin.table("user_criteria").select("*").eq("user_id", user_id).execute()
        if not criteria_response.data or len(criteria_response.data) == 0:
            return
        
        user_criteria = criteria_response.data[0]
        
        # Process each listing
        logging.info(f"Found {len(new_listings)} emails with listings to process")
        for listing in new_listings:
            urls_count = len(listing['urls'])
            logging.info(f"Processing email '{listing['subject']}' with {urls_count} URLs: {listing['urls']}")
            
            for idx, url in enumerate(listing['urls'], 1):
                try:
                    logging.info(f"[{idx}/{urls_count}] Processing URL: {url}")
                    
                    # Check if already exists (avoid duplicates)
                    existing = supabase_admin.table("processed_emails").select("*").eq("user_id", user_id).eq("listing_url", url).execute()
                    
                    if existing.data and len(existing.data) > 0:
                        existing_record = existing.data[0]
                        # Check if analysis already exists
                        if existing_record.get('analysis_result'):
                            logging.info(f"URL {url} already has analysis, skipping")
                            continue
                        else:
                            logging.info(f"URL {url} exists but no analysis yet, will retry analysis")
                    
                    # Mark email as processed (insert or update)
                    if not existing.data or len(existing.data) == 0:
                        supabase_admin.table("processed_emails").insert({
                            'user_id': user_id,
                            'email_message_id': listing['message_id'],
                            'email_subject': listing['subject'],
                            'email_from': listing['from'],
                            'listing_url': url,
                            'analysis_result': None  # Will be updated after analysis
                        }).execute()
                        logging.info(f"✓ Inserted processed_email record for URL {idx}/{urls_count}: {url}")
                    else:
                        logging.info(f"✓ Record already exists for URL {idx}/{urls_count}: {url}")
                    
                    # Trigger analysis (async) - use asyncio.create_task to run in background
                    asyncio.create_task(analyze_listing_from_email(user_id, url, user_criteria))
                    logging.info(f"✓ Started analysis task {idx}/{urls_count} for: {url}")
                    
                except Exception as e:
                    logging.error(f"✗ Error processing URL {idx}/{urls_count} ({url}): {str(e)}", exc_info=True)
                    continue
            
            logging.info(f"✓ Completed processing all {urls_count} URLs from email '{listing['subject']}'")
        
        # Update last_email_check timestamp
        supabase_admin.table("user_criteria").update({
            'last_email_check': datetime.utcnow().isoformat()
        }).eq("user_id", user_id).execute()
        
    except Exception as e:
        logging.error(f"Error in process_new_email_listings: {str(e)}")


async def analyze_listing_from_email(user_id: str, listing_url: str, user_criteria: dict):
    """Analyze a listing URL from email and store results"""
    try:
        logging.info(f"Starting analysis for URL: {listing_url}")
        
        # Scrape listing
        listing_data = call_firecrawl_scraper(listing_url)
        if "error" in listing_data:
            logging.error(f"Error scraping listing {listing_url}: {listing_data.get('error')}")
            # Store error in database
            supabase_admin.table("processed_emails").update({
                'analysis_result': {'error': listing_data.get('error'), 'url': listing_url}
            }).eq("user_id", user_id).eq("listing_url", listing_url).execute()
            return
        
        logging.info(f"Successfully scraped listing, generating report...")
        
        # Convert criteria to format expected by analysis
        criteria_text = json.dumps(user_criteria, default=str)
        
        # Analyze images
        image_analysis = analyze_images(listing_data.get('content', ''), max_images=3)
        
        # Generate match report
        match_report = generate_match_report(user_criteria, listing_data, image_analysis)
        
        logging.info(f"Generated match report (length: {len(match_report)}), storing in database...")
        
        # Store analysis result - use JSONB format
        analysis_data = {
            'report': match_report,
            'url': listing_url,
            'analyzed_at': datetime.utcnow().isoformat()
        }
        
        # Update the analysis_result field - use supabase_admin to bypass RLS
        try:
            update_result = supabase_admin.table("processed_emails").update({
                'analysis_result': analysis_data
            }).eq("user_id", user_id).eq("listing_url", listing_url).execute()
            
            if update_result.data and len(update_result.data) > 0:
                logging.info(f"Successfully stored analysis result for {listing_url}")
            else:
                logging.warning(f"No rows updated for {listing_url}, record might not exist")
                # Try to ensure the record exists by checking first
                check = supabase_admin.table("processed_emails").select("*").eq("user_id", user_id).eq("listing_url", listing_url).execute()
                if not check.data or len(check.data) == 0:
                    logging.error(f"Record doesn't exist for {listing_url}, cannot store analysis")
                else:
                    logging.info(f"Record exists, retrying update...")
                    update_result = supabase_admin.table("processed_emails").update({
                        'analysis_result': analysis_data
                    }).eq("user_id", user_id).eq("listing_url", listing_url).execute()
                    if update_result.data:
                        logging.info(f"Successfully stored analysis result on retry for {listing_url}")
        except Exception as db_error:
            logging.error(f"Database error storing analysis for {listing_url}: {str(db_error)}", exc_info=True)
            raise
        
    except Exception as e:
        logging.error(f"Error analyzing listing from email: {str(e)}", exc_info=True)
        # Try to store error in database
        try:
            supabase_admin.table("processed_emails").update({
                'analysis_result': {'error': str(e), 'url': listing_url}
            }).eq("user_id", user_id).eq("listing_url", listing_url).execute()
        except:
            pass
        # Try to store error in database
        try:
            supabase_admin.table("processed_emails").update({
                'analysis_result': {'error': str(e), 'url': listing_url}
            }).eq("user_id", user_id).eq("listing_url", listing_url).execute()
        except:
            pass


@app.post("/api/user/criteria", response_model=UserCriteriaResponse)
async def create_user_criteria(
    criteria: UserCriteriaRequest,
    user_id: str = Depends(verify_token)
):
    """Create or update user criteria"""
    try:
        # Use service role client for backend operations (bypasses RLS since we verify JWT ourselves)
        # Check if criteria already exists
        existing = supabase_admin.table("user_criteria").select("*").eq("user_id", user_id).execute()
        
        criteria_data = criteria.dict(exclude_none=True)
        criteria_data["user_id"] = user_id
        
        # Handle app_password: only update if provided, otherwise keep existing
        app_password = criteria_data.pop('email_app_password', None)
        
        if existing.data and len(existing.data) > 0:
            # Update existing
            criteria_id = existing.data[0]["id"]
            criteria_data["updated_at"] = datetime.utcnow().isoformat()
            # Only update password if a new one is provided
            if app_password:
                criteria_data["email_app_password"] = app_password
            # If app_password is None, don't include it - this preserves the existing password
            response = supabase_admin.table("user_criteria").update(criteria_data).eq("id", criteria_id).execute()
        else:
            # Create new
            criteria_data["created_at"] = datetime.utcnow().isoformat()
            criteria_data["updated_at"] = datetime.utcnow().isoformat()
            if app_password:
                criteria_data["email_app_password"] = app_password
            response = supabase_admin.table("user_criteria").insert(criteria_data).execute()
        
        if response.data and len(response.data) > 0:
            result = response.data[0].copy()
            # Remove app_password from response for security
            result.pop('email_app_password', None)
            return UserCriteriaResponse(**result)
        else:
            raise HTTPException(status_code=500, detail="Failed to save criteria")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving criteria: {str(e)}")


@app.put("/api/user/criteria", response_model=UserCriteriaResponse)
async def update_user_criteria(
    criteria: UserCriteriaRequest,
    user_id: str = Depends(verify_token)
):
    """Update user criteria"""
    try:
        criteria_data = criteria.dict(exclude_none=True)
        criteria_data["updated_at"] = datetime.utcnow().isoformat()
        
        # Handle app_password separately
        app_password = criteria_data.pop('email_app_password', None)
        if app_password:
            criteria_data["email_app_password"] = app_password
        
        response = supabase_admin.table("user_criteria").update(criteria_data).eq("user_id", user_id).execute()
        
        if response.data and len(response.data) > 0:
            result = response.data[0].copy()
            # Remove app_password from response for security
            result.pop('email_app_password', None)
            return UserCriteriaResponse(**result)
        else:
            raise HTTPException(status_code=404, detail="No criteria found to update")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating criteria: {str(e)}")


@app.post("/api/user/check-email")
async def check_email_manual(
    background_tasks: BackgroundTasks,
    user_id: str = Depends(verify_token)
):
    """Manually trigger email check"""
    try:
        # Get user criteria with email settings
        criteria_response = supabase_admin.table("user_criteria").select("*").eq("user_id", user_id).execute()
        
        if not criteria_response.data or len(criteria_response.data) == 0:
            raise HTTPException(status_code=404, detail="No criteria found")
        
        user_criteria = criteria_response.data[0]
        
        if not user_criteria.get('email_monitoring_enabled'):
            raise HTTPException(status_code=400, detail="Email monitoring is not enabled")
        
        email_address = user_criteria.get('monitor_email')
        app_password = user_criteria.get('email_app_password')
        email_provider = user_criteria.get('email_provider', 'gmail')
        email_sender = user_criteria.get('email_sender')
        email_subject_keywords = user_criteria.get('email_subject_keywords')
        
        missing_fields = []
        if not email_address:
            missing_fields.append("Email Address to Monitor")
        if not app_password:
            missing_fields.append("App Password")
        
        if missing_fields:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required fields: {', '.join(missing_fields)}"
            )
        
        # Check for pending analyses and retry them
        try:
            pending_analyses = supabase_admin.table("processed_emails").select("*").eq("user_id", user_id).is_("analysis_result", "null").execute()
            if pending_analyses.data and len(pending_analyses.data) > 0:
                logger.info(f"Found {len(pending_analyses.data)} pending analyses, retrying...")
                for pending in pending_analyses.data:
                    listing_url = pending.get('listing_url')
                    if listing_url:
                        logger.info(f"Retrying analysis for {listing_url}")
                        asyncio.create_task(analyze_listing_from_email(user_id, listing_url, user_criteria))
        except Exception as e:
            logger.warning(f"Error checking for pending analyses: {str(e)}")
        
        # Trigger email check in background with configured filters
        background_tasks.add_task(
            process_new_email_listings,
            user_id,
            email_address,
            app_password,
            email_provider,
            email_sender,
            email_subject_keywords
        )
        
        return {"status": "success", "message": "Email check started. Retrying any pending analyses..."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking email: {str(e)}")


@app.get("/api/user/analyses")
async def get_email_analyses(
    user_id: str = Depends(verify_token),
    limit: int = 50
):
    """Get email analysis results for the user"""
    try:
        # Use service role client for backend operations (bypasses RLS since we verify JWT ourselves)
        # Get all processed emails with analysis results for this user
        # Note: Column is 'processed_at' not 'created_at'
        # Try ordering by processed_at descending
        try:
            response = supabase_admin.table("processed_emails").select("*").eq("user_id", user_id).order("processed_at", desc=True).limit(limit).execute()
        except Exception as order_error:
            # If ordering fails, try without order or with different syntax
            logging.warning(f"Ordering failed, trying without order: {str(order_error)}")
            response = supabase_admin.table("processed_emails").select("*").eq("user_id", user_id).limit(limit).execute()
        
        analyses = []
        pending_analyses = []
        if response.data:
            logging.info(f"Found {len(response.data)} processed email records")
            for item in response.data:
                analysis_result = item.get('analysis_result')
                listing_url = item.get('listing_url')
                
                # Track pending analyses (record exists but no analysis_result yet)
                if not analysis_result:
                    pending_analyses.append({
                        'id': str(item.get('id')),
                        'listing_url': listing_url,
                        'email_subject': item.get('email_subject') or 'No subject',
                        'email_from': item.get('email_from') or 'Unknown',
                        'created_at': item.get('processed_at') or item.get('created_at'),
                        'status': 'pending'
                    })
                    logging.debug(f"Analysis pending for {listing_url}")
                    continue
                
                # Handle both dict and string formats for analysis_result
                if isinstance(analysis_result, str):
                    try:
                        analysis_result = json.loads(analysis_result)
                    except json.JSONDecodeError:
                        logging.warning(f"Failed to parse analysis_result as JSON: {str(analysis_result)[:100]}")
                        analysis_result = {}
                elif not isinstance(analysis_result, dict):
                    analysis_result = {}
                
                # Check for errors
                if analysis_result.get('error'):
                    logging.warning(f"Analysis error for {listing_url}: {analysis_result.get('error')}")
                    pending_analyses.append({
                        'id': str(item.get('id')),
                        'listing_url': listing_url,
                        'email_subject': item.get('email_subject') or 'No subject',
                        'email_from': item.get('email_from') or 'Unknown',
                        'created_at': item.get('processed_at') or item.get('created_at'),
                        'status': 'error',
                        'error': analysis_result.get('error')
                    })
                    continue
                
                # Only include items that have a report
                if analysis_result and analysis_result.get('report'):
                    analyses.append({
                        'id': str(item.get('id')),
                        'listing_url': listing_url,
                        'email_subject': item.get('email_subject') or 'No subject',
                        'email_from': item.get('email_from') or 'Unknown',
                        'created_at': item.get('processed_at') or item.get('created_at'),
                        'report': analysis_result.get('report'),
                        'url': analysis_result.get('url', listing_url),
                        'status': 'completed'
                    })
        
        logging.info(f"Returning {len(analyses)} completed analyses, {len(pending_analyses)} pending")
        
        # Sort analyses by processed_at descending if we couldn't order in query
        if analyses and not any('processed_at' in str(a.get('created_at', '')) for a in analyses[:1]):
            analyses.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        # Sort pending analyses too
        if pending_analyses:
            pending_analyses.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        # Always return success, even if no analyses found
        return {
            "analyses": analyses, 
            "count": len(analyses),
            "pending": pending_analyses,
            "pending_count": len(pending_analyses)
        }
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logging.error(f"Error retrieving analyses: {error_msg}")
        import traceback
        logging.error(traceback.format_exc())
        
        # Provide more helpful error messages
        if "does not exist" in error_msg.lower() or "relation" in error_msg.lower() or "table" in error_msg.lower():
            raise HTTPException(
                status_code=500, 
                detail="The processed_emails table does not exist. Please run the database migration: supabase_schema_email.sql in your Supabase SQL Editor."
            )
        elif "permission" in error_msg.lower() or "policy" in error_msg.lower() or "row level security" in error_msg.lower():
            raise HTTPException(
                status_code=500,
                detail="Permission denied. Please ensure Row Level Security policies are set up correctly for the processed_emails table."
            )
        elif "not found" in error_msg.lower() or "404" in error_msg.lower():
            # If table doesn't exist or no records, return empty list instead of error
            logging.warning("No analyses found or table doesn't exist, returning empty list")
            return {"analyses": [], "count": 0}
        else:
            error_detail = f"Error retrieving analyses: {error_msg}"
            if hasattr(e, 'message'):
                error_detail += f" - {e.message}"
            raise HTTPException(status_code=500, detail=error_detail)


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, user_id: str = Depends(verify_token)):
    """
    Process a chat message with apartment criteria. Optionally analyze a listing URL if provided.
    """
    try:
        # Extract URL from message (optional)
        user_message, listing_url = extract_url_from_message(request.message)
        
        # Step 1: Extract user criteria from the message
        criteria = extract_criteria_with_openai(user_message)
        if "error" in criteria:
            raise HTTPException(status_code=500, detail=f"Error extracting criteria: {criteria['error']}")
        
        # Step 2: Save criteria to user profile automatically
        save_success = False
        save_error_message = None
        try:
            # Use service role client for backend operations (bypasses RLS since we verify JWT ourselves)
            logger.info(f"Using supabase_admin client (service key: {'SET' if SUPABASE_SERVICE_KEY else 'NOT SET'})")
            # Check if criteria already exists
            existing = supabase_admin.table("user_criteria").select("*").eq("user_id", user_id).execute()
            
            # Prepare criteria data - only include fields that exist in the schema
            # Map OpenAI extracted fields to database fields
            additional_reqs = criteria.get('additional_requirements') or criteria.get('user_additional_requirements')
            # Convert array to dict if needed, or keep as dict
            if isinstance(additional_reqs, list):
                # Convert array to dict format
                additional_reqs = {"requirements": additional_reqs}
            elif additional_reqs and not isinstance(additional_reqs, dict):
                # If it's a string or other type, wrap it
                additional_reqs = {"requirements": [str(additional_reqs)]}
            
            criteria_data = {
                "user_id": user_id,
                "property_type": criteria.get('property_type'),
                "location": criteria.get('location'),
                "min_rooms": criteria.get('min_rooms'),
                "max_rooms": criteria.get('max_rooms'),
                "min_living_space": criteria.get('min_living_space'),
                "max_living_space": criteria.get('max_living_space'),
                "min_rent": criteria.get('min_rent'),
                "max_rent": criteria.get('max_rent'),
                "occupants": criteria.get('occupants'),
                "duration": criteria.get('duration'),
                "starting_when": criteria.get('starting_when'),
            }
            
            # Add additional_requirements only if it exists
            if additional_reqs:
                criteria_data["user_additional_requirements"] = additional_reqs
            
            # Remove None values (but keep empty strings and 0)
            criteria_data = {k: v for k, v in criteria_data.items() if v is not None}
            
            logger.info(f"Saving criteria for user {user_id}: {criteria_data}")
            
            if existing.data and len(existing.data) > 0:
                # Update existing
                criteria_id = existing.data[0]["id"]
                criteria_data["updated_at"] = datetime.utcnow().isoformat()
                response = supabase_admin.table("user_criteria").update(criteria_data).eq("id", criteria_id).execute()
                logger.info(f"Updated criteria for user {user_id}, response data: {response.data}")
            else:
                # Create new
                criteria_data["created_at"] = datetime.utcnow().isoformat()
                criteria_data["updated_at"] = datetime.utcnow().isoformat()
                response = supabase_admin.table("user_criteria").insert(criteria_data).execute()
                logger.info(f"Created new criteria for user {user_id}, response data: {response.data}")
                
            if not response.data or len(response.data) == 0:
                error_msg = "Database save returned no data"
                logger.error(f"Failed to save criteria - {error_msg}")
                raise Exception(error_msg)
            
            logger.info(f"Successfully saved criteria for user {user_id}")
            save_success = True
                
        except Exception as save_error:
            error_msg = f"Failed to save criteria: {str(save_error)}"
            logger.error(error_msg, exc_info=True)
            save_success = False
            save_error_message = str(save_error)
        
        # Step 3: If URL provided, analyze the listing
        if listing_url:
            # Scrape listing
            listing_data = call_firecrawl_scraper(listing_url)
            if "error" in listing_data:
                return ChatResponse(
                    response=f"✅ Your preferences have been saved to your profile!\n\nHowever, I couldn't analyze the listing URL: {listing_data['error']}\n\nYou can view and edit your saved preferences in your Profile page.",
                    status="success"
                )
            
            # Analyze images (optional, can be skipped for speed)
            print(f"[Debug] Starting image analysis...")
            image_analysis = analyze_images(listing_data.get('content', ''), max_images=3)
            print(f"[Debug] Image analysis length: {len(image_analysis)}")
            print(f"[Debug] Image analysis result: {image_analysis[:500]}...")  # First 500 chars
            print(f"[Debug] Image analysis is valid: {image_analysis not in ['No images found to analyze', 'Image analysis skipped (no API key)']}")
            
            # Generate match report
            print(f"[Debug] Generating match report with image_analysis={bool(image_analysis)}")
            match_report = generate_match_report(criteria, listing_data, image_analysis)
            
            return ChatResponse(
                response=match_report,
                status="success"
            )
        else:
            # No URL provided - just confirm criteria was saved
            criteria_summary = []
            if criteria.get('property_type'):
                criteria_summary.append(f"**Property Type:** {criteria['property_type'].title()}")
            if criteria.get('location'):
                criteria_summary.append(f"**Location:** {criteria['location']}")
            if criteria.get('min_rooms') or criteria.get('max_rooms'):
                rooms = []
                if criteria.get('min_rooms'):
                    rooms.append(f"{criteria['min_rooms']}+")
                if criteria.get('max_rooms'):
                    rooms.append(f"up to {criteria['max_rooms']}")
                criteria_summary.append(f"**Rooms:** {' '.join(rooms)}")
            if criteria.get('min_living_space') or criteria.get('max_living_space'):
                space = []
                if criteria.get('min_living_space'):
                    space.append(f"{criteria['min_living_space']}m²+")
                if criteria.get('max_living_space'):
                    space.append(f"up to {criteria['max_living_space']}m²")
                criteria_summary.append(f"**Living Space:** {' '.join(space)}")
            if criteria.get('min_rent') or criteria.get('max_rent'):
                price_label = "Rent" if criteria.get('property_type') == 'rent' else "Price"
                price = []
                if criteria.get('min_rent'):
                    price.append(f"CHF {criteria['min_rent']}+")
                if criteria.get('max_rent'):
                    price.append(f"up to CHF {criteria['max_rent']}")
                criteria_summary.append(f"**{price_label}:** {' '.join(price)}")
            
            summary_text = "\n".join(criteria_summary) if criteria_summary else "Your preferences"
            
            if save_success:
                return ChatResponse(
                    response=f"""✅ **Your preferences have been saved!**

{summary_text}

You can:
- **View and edit** your preferences in your [Profile page](/profile)
- **Add a listing URL** to analyze a specific property
- **Set up email monitoring** in your Profile to automatically analyze new listings

To analyze a specific listing, just paste a URL from any property website along with your message!""",
                    status="success"
                )
            else:
                return ChatResponse(
                    response=f"""⚠️ **Preferences extracted but couldn't be saved automatically**

{summary_text}

**Please save manually:** Go to your [Profile page](/profile) and click "Save Criteria" to save these preferences.

Error: {save_error_message}""",
                    status="warning"
                )
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] Exception in /api/chat endpoint:")
        print(error_details)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/profile", response_class=HTMLResponse)
async def read_profile():
    """Serve the profile page"""
    with open("static/profile.html", "r") as f:
        return f.read()


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page"""
    with open("static/index.html", "r") as f:
        return f.read()


# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


async def periodic_email_check():
    """Background task to periodically check emails for all users with monitoring enabled"""
    while True:
        try:
            # Get all users with email monitoring enabled
            response = supabase_admin.table("user_criteria").select("*").eq("email_monitoring_enabled", True).execute()
            
            if response.data:
                for user_criteria in response.data:
                    user_id = user_criteria.get('user_id')
                    email_address = user_criteria.get('monitor_email')
                    app_password = user_criteria.get('email_app_password')
                    email_provider = user_criteria.get('email_provider', 'gmail')
                    email_sender = user_criteria.get('email_sender')
                    email_subject_keywords = user_criteria.get('email_subject_keywords')
                    
                    if email_address and app_password:
                        try:
                            await process_new_email_listings(user_id, email_address, app_password, email_provider, email_sender, email_subject_keywords)
                        except Exception as e:
                            logger.error(f"Error checking email for user {user_id}: {str(e)}")
            
            # Wait 5 minutes before next check
            await asyncio.sleep(300)
            
        except Exception as e:
            logger.error(f"Error in periodic email check: {str(e)}")
            await asyncio.sleep(60)  # Wait 1 minute on error


@app.on_event("startup")
async def startup_event():
    """Start background tasks on application startup"""
    asyncio.create_task(periodic_email_check())
    logger.info("Email monitoring background task started")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

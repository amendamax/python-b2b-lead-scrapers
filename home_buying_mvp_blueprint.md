# Technical Architecture Blueprint: Home-Buying Journey Orchestrator (MVP)

This document outlines the technical foundation, database schema, and backend architecture designed for the Home-Buying Journey Orchestrator MVP. 

The primary goal of this MVP is to establish a modular, scalable horizontal layer that guides home buyers through their journey, integrates a context-aware AI assistant, and prepares the data ingestion pipeline for property platforms.

---

## 🛠️ Technology Stack Recommendations

*   **Backend:** Python 3.11+ with **FastAPI** (High performance, automatic interactive docs, native async support, and excellent integration with AI libraries).
*   **Database:** **PostgreSQL** (Robust relational database, ideal for handling structured user data, checklist states, and document metadata).
*   **ORM:** **SQLAlchemy 2.0** with **Alembic** (For clean, database-agnostic models and robust migrations).
*   **AI Integration:** **Gemini API (via Google GenAI SDK)** or **OpenAI API** (Using structured outputs/Pydantic schemas for predictable assistant behavior).
*   **Hosting/Cloud:** **AWS S3** (Secure, encrypted document vault) + **DigitalOcean / AWS EC2** (Simple application hosting).

---

## 🗄️ Database Schema (Entity Relationship)

Below is the structured SQL schema design for the PostgreSQL database, showing how the user's state, checklist roadmap, document vault, and AI assistant history are linked.

```sql
-- 1. Users Table (Core Profile & Financial Status)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    target_budget NUMERIC(12, 2) DEFAULT 0.00,
    savings_amount NUMERIC(12, 2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Roadmap Milestones Definition (Pre-seeded templates)
CREATE TABLE roadmap_milestones (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    order_index INT UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. User Milestone Progress (Tracks which milestones the user is currently working on)
CREATE TABLE user_milestones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    milestone_id INT REFERENCES roadmap_milestones(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'PENDING', -- PENDING, IN_PROGRESS, COMPLETED
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_user_milestone UNIQUE (user_id, milestone_id)
);

-- 4. User Milestone Tasks (Checklist items inside each milestone)
CREATE TABLE user_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_milestone_id UUID REFERENCES user_milestones(id) ON DELETE CASCADE,
    task_name VARCHAR(255) NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    notes TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Properties Table (Saves property links and details pasted by the user)
CREATE TABLE properties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    url TEXT,
    price NUMERIC(12, 2),
    address VARCHAR(255),
    status VARCHAR(50) DEFAULT 'LIKED', -- LIKED, UNDER_OFFER, ARCHIVED
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. Document Vault (Metadata for uploaded PDFs)
CREATE TABLE document_vault (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    s3_key VARCHAR(512) NOT NULL, -- Path to the encrypted file in AWS S3
    document_type VARCHAR(100), -- e.g. ID_PROOF, BANK_STATEMENT, MORTGAGE_DIP
    upload_status VARCHAR(50) DEFAULT 'UPLOADED', -- UPLOADED, PARSING_PENDING, VERIFIED
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. AI Assistant History (For storing chatbot conversations)
CREATE TABLE ai_assistant_chats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    sender VARCHAR(50) NOT NULL, -- USER or ASSISTANT
    current_milestone_id INT REFERENCES roadmap_milestones(id), -- Contextual step when the message was sent
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

---

## 📂 Backend Project Structure (FastAPI)

```text
home_buying_orchestrator/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application startup
│   │
│   ├── api/                    # API Endpoints (Controllers)
│   │   ├── auth.py             # User login and registration
│   │   ├── roadmap.py          # Checklist and milestone tracking
│   │   ├── vault.py            # File upload and secure download URLs
│   │   ├── properties.py       # Ingested property records
│   │   └── assistant.py        # AI Assistant chat gateway
│   │
│   ├── core/                   # Application Config, Security & Database Init
│   │   ├── config.py           # Environment variables (DB URI, API Keys)
│   │   ├── database.py         # SQLAlchemy engine and sessionmaker
│   │   └── security.py         # JWT Token creation and hashing
│   │
│   ├── models/                 # SQLAlchemy DB Models
│   │   └── schemas.py          # Unified Pydantic models (data validation)
│   │
│   └── services/               # Internal business logic layers
│       ├── ai_service.py       # LLM orchestrator & structured prompt builder
│       └── scraper_service.py  # Property extraction manager (ZenRows / ScraperAPI)
│
├── requirements.txt
└── alembic.ini
```

---

## 🤖 Context-Aware AI Assistant Strategy

To build a **guided AI assistant**, we don't just send the user's message to ChatGPT. We inject the user's current roadmap status so the AI knows exactly where the user stands in their home-buying journey.

### Example: Injecting Context into the LLM Prompt (Python Service)

```python
# app/services/ai_service.py
import openai
from app.core.config import settings

class AIService:
    @staticmethod
    async def get_guided_response(user_message: str, current_milestone: str, completed_tasks: list, pending_tasks: list):
        # 1. System Prompt establishes context and constraints
        system_prompt = f"""
You are an expert UK Home-Buying Assistant. Your job is to guide the user through their home-buying roadmap.
The user is currently in the milestone: "{current_milestone}".

Their progress on this milestone:
- Completed Tasks: {', '.join(completed_tasks) if completed_tasks else 'None'}
- Pending Tasks: {', '.join(pending_tasks) if pending_tasks else 'None'}

Always provide helpful, actionable advice tailored to their CURRENT milestone. 
Keep your answers structured, using bullet points where appropriate.
Avoid advice about future milestones unless they ask, keep them focused on completing the current step.
"""
        
        # 2. Call the AI model
        response = await openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Highly cost-efficient, fast model for MVP
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7
        )
        
        return response.choices[0].message['content'].strip()
```

---

## ⚙️ Data Ingestion Pipeline (Modular Scraper Setup)

To ingest property data without getting blocked by UK platforms (e.g. Rightmove, Zoopla), the MVP will route requests through a managed scraping proxy. Below is the blueprint of the scraper service.

```python
# app/services/scraper_service.py
import httpx
from bs4 import BeautifulSoup
from app.core.config import settings

class ScraperService:
    @staticmethod
    async def extract_property_details(url: str) -> dict:
        # Route requests through a scraping API (e.g., ZenRows / ScraperAPI) to bypass Cloudflare
        proxy_url = "https://api.scraperapi.com"
        params = {
            "api_key": settings.SCRAPER_API_KEY,
            "url": url,
            "render": "false"  # Keep HTML loading lightweight
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(proxy_url, params=params, timeout=20.0)
            if response.status_code != 200:
                raise Exception("Failed to retrieve property details from source.")
            
            # Simple parse logic (can be extended with specific site selectors)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Placeholder selector logic for MVP demo (Rightmove example)
            price_element = soup.select_one(".ot1981") or soup.select_one("[data-testid='price']")
            price_text = price_element.text if price_element else "0.00"
            
            address_element = soup.select_one("h1") or soup.select_one("[data-testid='address']")
            address_text = address_element.text if address_element else "Unknown Address"
            
            # Sanitize price string to numeric
            clean_price = ''.join(filter(str.isdigit, price_text))
            
            return {
                "title": "Ingested Property Details",
                "price": float(clean_price) if clean_price else 0.00,
                "address": address_text.strip(),
                "url": url
            }
```

---

## 📋 Roadmap Tasks Pre-Population (Seeding)

To make the dashboard immediately useful for onboarding, the system will pre-seed the database with the standard steps:

1.  **Step 1: Financial Setup & Readiness**
    *   [ ] Calculate target deposit
    *   [ ] Check credit report (Experian/Equifax)
    *   [ ] Upload bank statements to Vault
2.  **Step 2: Mortgage Pre-Approval**
    *   [ ] Consult mortgage advisor
    *   [ ] Get Mortgage Decision in Principle (DIP)
    *   [ ] Save DIP document in Vault
3.  **Step 3: Property Hunting**
    *   [ ] Link liked properties from platforms
    *   [ ] Schedule property viewings
    *   [ ] Compare affordability indicators
4.  **Step 4: Offer & Solicitor Engagement**
    *   [ ] Make an offer on chosen property
    *   [ ] Offer Accepted - secure documentation
    *   [ ] Instruct a licensed conveyancing solicitor

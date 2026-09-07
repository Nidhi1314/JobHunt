# JobHunt AI 🎯

An agentic job search system built with **LangGraph + FastAPI + React** that automates job discovery for college students.

Instead of manually visiting 10+ company career pages every day, JobHunt AI sends a **daily email with new, AI-ranked job listings** matched to your role, graduation year, and preferences — automatically.

---

## What it does

- 🕷️ Crawls **10 company career portals** (Google, Amazon, Microsoft, Flipkart, Swiggy, Zomato, Razorpay, CRED, TCS, Infosys) using Playwright
- 🤖 Runs a **4-agent LangGraph pipeline**: Crawler → Filter → Research → Report
- 🔴 **Hard filters** out senior roles and wrong batch years automatically
- 🟡 **Soft scores** each job 0–10 with Groq LLM based on your profile
- 💰 Estimates **missing salary data** via Tavily → Glassdoor/AmbitionBox
- 📧 Sends a **beautiful dark-themed email** with only new listings (no duplicates)
- 🗄️ Stores all jobs in **SQLite** with deduplication across runs
- ⏰ Runs automatically every morning via **APScheduler**
- 🎨 Full **React dashboard** to view jobs, manage profile, and trigger pipeline manually

---

## Tech Stack

| Layer | Tech |
|---|---|
| Agent Orchestration | LangGraph |
| LLM | Groq (Llama 3.1 70B) — Free |
| Web Crawling | Playwright + BeautifulSoup |
| Search Fallback | Tavily API |
| Backend | FastAPI (Python 3.9+) |
| Frontend | React + Vite |
| Email Alerts | Gmail SMTP (aiosmtplib) |
| Scheduler | APScheduler |
| Database | SQLite (SQLModel) |

---

## Project Structure

```
job hunt/
├── backend/
│   ├── agents/          # 4 LangGraph agents
│   │   ├── crawler_agent.py
│   │   ├── filter_agent.py
│   │   ├── research_agent.py
│   │   └── report_agent.py
│   ├── crawlers/        # Company-specific crawlers
│   │   ├── base_crawler.py
│   │   ├── registry.py
│   │   ├── tavily_fallback.py
│   │   └── companies/   # 10 crawlers (google, amazon, ...)
│   ├── graph/           # LangGraph pipeline wiring
│   │   └── pipeline.py
│   ├── email_sender/    # Gmail SMTP email builder
│   ├── scheduler/       # APScheduler daily job
│   ├── api/             # FastAPI routes
│   ├── db/              # SQLite setup
│   ├── models/          # SQLModel schemas
│   ├── config.py        # Pydantic settings
│   └── main.py          # FastAPI app entry point
├── frontend/            # React + Vite dashboard
│   └── src/
│       ├── pages/       # Dashboard, Jobs, Profile, Pipeline
│       └── App.jsx
├── .env                 # API keys (not committed)
├── requirements.txt
└── jobhunt.db           # SQLite database (auto-created)
```

---

## Setup

### 1. Clone & create virtual environment

```bash
git clone <repo>
cd "job hunt"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure `.env`

```env
# LLM (free at console.groq.com)
GROQ_API_KEY=gsk_xxxxxxxxxxxx

# Web Search fallback (free at app.tavily.com)
TAVILY_API_KEY=tvly-xxxxxxxxxxxx

# Gmail SMTP (create App Password at myaccount.google.com/apppasswords)
GMAIL_USER=your@gmail.com
GMAIL_APP_PASSWORD=xxxxxxxxxxxx
ALERT_TO_EMAIL=your@gmail.com

# Schedule (24h format — 8:00 AM by default)
PIPELINE_SCHEDULE_HOUR=8
PIPELINE_SCHEDULE_MINUTE=0
```

### 3. Start the backend

```bash
source .venv/bin/activate
uvicorn backend.main:app --reload
# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### 4. Start the frontend

```bash
cd frontend
npm install
npm run dev
# Dashboard at http://localhost:5173
```

---

## Usage

### Option A — Dashboard (recommended)
1. Open `http://localhost:5173`
2. Go to **Profile** → set your grad year, preferred roles, locations
3. Go to **Pipeline** → click **🚀 Start Pipeline**
4. Check your inbox for the job digest email

### Option B — Command line
```bash
# Run pipeline once
python test_pipeline.py

# Test email only
python test_email.py

# Test a single crawler
python test_crawlers.py
```

---

## How the Pipeline Works

```
[Crawler Agent]     →  Runs all 10 crawlers in parallel (Playwright)
                        Falls back to Tavily if a site blocks us
      ↓
[Filter Agent]      →  Hard filter: removes senior/wrong-batch roles
                        Soft filter: Groq LLM scores each job 0–10
      ↓
[Research Agent]    →  Fetches estimated salary for jobs missing pay data
      ↓
[Report Agent]      →  Deduplicates against DB, saves new jobs, sends email
```

---

## Filter Logic

**Hard Filters** (auto-discard):
- Job explicitly mentions a different graduation batch year
- Job title contains senior/lead/principal/5+ years experience keywords

**Soft Scoring** (LLM, 0–10):
- Role title match (40%)
- Location match (20%)
- Work mode match (15%)
- Salary estimate (15%)
- Company type match (10%)

Only jobs scoring ≥ 5.0 (configurable in Profile) are included in the email.

---

## Companies Covered

| Company | Type | Fallback |
|---------|------|---------|
| Google | Product | Tavily |
| Amazon | Product | Tavily |
| Microsoft | Product | Tavily |
| Flipkart | Product | Tavily |
| Swiggy | Product | Tavily |
| Zomato | Product | Tavily |
| Razorpay | Startup | Tavily |
| CRED | Startup | Tavily |
| TCS | Service | Tavily |
| Infosys | Service | Tavily |

---

*Built for personal use · Not for commercial redistribution*

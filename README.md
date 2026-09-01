# JobHunt AI 🎓

An agentic job search system built with **LangGraph + FastAPI + React** 
that automates job discovery for college students.

Instead of manually visiting 25+ company career pages every day, 
JobHunt AI sends a **daily email with new job listings** matched to 
your role, graduation year, and expected salary — automatically.

## What it does
- 🔍 Crawls **25+ company career portals** directly (Google, Amazon, Flipkart, TCS...)
- 🤖 Uses a **4-agent LangGraph pipeline** to crawl → filter → research → report
- 💰 Estimates **missing salary data** via Glassdoor/AmbitionBox web research
- 📧 Sends **daily email alerts** with only new listings (no duplicates)
- ⚡ Powered by **Groq (Llama 3.1 70B)** — completely free to run

## Tech Stack
| Layer | Tech |
|---|---|
| Agent Orchestration | LangGraph |
| LLM | Groq (Llama 3.1 70B) — Free |
| Web Crawling | Playwright + BeautifulSoup |
| Job Search Fallback | Tavily API |
| Backend | FastAPI (Python) |
| Frontend | React (Vite) |
| Alerts | Gmail SMTP + APScheduler |
| Job History | SQLite |
| Observability | LangSmith |

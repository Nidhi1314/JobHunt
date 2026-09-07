from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from backend.agents.crawler_agent import run_crawler_agent
from backend.agents.filter_agent import run_filter_agent
from backend.agents.research_agent import run_research_agent
from backend.agents.report_agent import run_report_agent
from backend.models.schemas import UserProfile
from sqlmodel import Session, select
from backend.db.database import engine
from rich.console import Console

console = Console()


# ── State Schema ──────────────────────────────────────────────────────────────

class PipelineState(TypedDict):
    profile: Dict[str, Any]       # user preferences
    raw_jobs: List[Dict]          # from crawler agent
    filtered_jobs: List[Dict]     # after filter agent
    enriched_jobs: List[Dict]     # after research agent
    new_jobs: List[Dict]          # after dedup (report agent)
    jobs_crawled: int
    jobs_after_filter: int
    jobs_new: int
    email_ready: bool
    error: Optional[str]


# ── Build Graph ───────────────────────────────────────────────────────────────

def build_pipeline() -> StateGraph:
    graph = StateGraph(PipelineState)

    graph.add_node("crawler", run_crawler_agent)
    graph.add_node("filter", run_filter_agent)
    graph.add_node("research", run_research_agent)
    graph.add_node("report", run_report_agent)

    graph.set_entry_point("crawler")
    graph.add_edge("crawler", "filter")
    graph.add_edge("filter", "research")
    graph.add_edge("research", "report")
    graph.add_edge("report", END)

    return graph.compile()


# ── Load Profile from DB ──────────────────────────────────────────────────────

def load_profile() -> Dict[str, Any]:
    with Session(engine) as session:
        profile = session.exec(select(UserProfile)).first()
        if not profile:
            return {
                "grad_year": "2025",
                "preferred_roles": "SDE,Software Engineer",
                "min_salary_lpa": 0,
                "preferred_locations": "",
                "preferred_work_mode": "",
                "preferred_company_types": "",
                "alert_email": "",
                "relevance_threshold": 5.0,
            }
        return {
            "grad_year": profile.grad_year,
            "preferred_roles": profile.preferred_roles,
            "min_salary_lpa": profile.min_salary_lpa,
            "preferred_locations": profile.preferred_locations,
            "preferred_work_mode": profile.preferred_work_mode,
            "preferred_company_types": profile.preferred_company_types,
            "alert_email": profile.alert_email,
            "relevance_threshold": profile.relevance_threshold,
        }


# ── Run Pipeline ──────────────────────────────────────────────────────────────

async def run_pipeline() -> Dict[str, Any]:
    """Main entry point to run the full 4-agent pipeline."""
    console.print("\n[bold magenta]🚀 JobHunt AI Pipeline Starting...[/bold magenta]\n")

    pipeline = build_pipeline()
    profile = load_profile()

    initial_state: PipelineState = {
        "profile": profile,
        "raw_jobs": [],
        "filtered_jobs": [],
        "enriched_jobs": [],
        "new_jobs": [],
        "jobs_crawled": 0,
        "jobs_after_filter": 0,
        "jobs_new": 0,
        "email_ready": False,
        "error": None,
    }

    result = await pipeline.ainvoke(initial_state)

    console.print("\n[bold magenta]✨ Pipeline Complete![/bold magenta]")
    console.print(f"  Crawled:    {result['jobs_crawled']} jobs")
    console.print(f"  Filtered:   {result['jobs_after_filter']} jobs")
    console.print(f"  New:        {result['jobs_new']} jobs")
    console.print(f"  Email ready: {result['email_ready']}")

    return result

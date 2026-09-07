import re
from typing import List, Dict, Any, Optional, Tuple
from backend.config import get_settings
from rich.console import Console

console = Console()
settings = get_settings()


def extract_salary_from_text(text: str) -> tuple:

    """
    Extract salary range from text like "₹8-12 LPA", "8 to 15 lakh", "CTC 10 LPA".
    Returns (min_lpa, max_lpa).
    """
    text = text.lower()
    patterns = [
        r"₹?\s*(\d+(?:\.\d+)?)\s*[-–to]+\s*(\d+(?:\.\d+)?)\s*(?:lpa|lakh|l)",
        r"(\d+(?:\.\d+)?)\s*[-–to]+\s*(\d+(?:\.\d+)?)\s*(?:lpa|lakh|l)",
        r"(?:ctc|salary|package)[^\d]*(\d+(?:\.\d+)?)\s*(?:lpa|lakh|l)",
        r"(\d+(?:\.\d+)?)\s*(?:lpa|lakh per annum)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            groups = match.groups()
            if len(groups) == 2:
                return float(groups[0]), float(groups[1])
            elif len(groups) == 1:
                val = float(groups[0])
                return val, val
    return None, None


async def run_research_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agent 3: For jobs missing salary data, search Glassdoor/AmbitionBox via Tavily.
    Enriches jobs with estimated salary range.
    """
    console.print("\n[bold blue]═══ Agent 3: Research Agent ═══[/bold blue]")

    filtered_jobs: List[Dict[str, Any]] = state.get("filtered_jobs", [])

    if not filtered_jobs:
        return {**state, "enriched_jobs": []}

    # Only research jobs that are missing salary
    missing_salary = [
        j for j in filtered_jobs
        if j.get("salary_min") is None and j.get("salary_max") is None
    ]

    console.print(
        f"[cyan]{len(missing_salary)}/{len(filtered_jobs)} jobs missing salary "
        f"→ researching via Tavily[/cyan]"
    )

    if not missing_salary or not settings.tavily_api_key:
        if not settings.tavily_api_key:
            console.print("[yellow]⚠️  No Tavily key — skipping salary research[/yellow]")
        return {**state, "enriched_jobs": filtered_jobs}

    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=settings.tavily_api_key)
    except ImportError:
        return {**state, "enriched_jobs": filtered_jobs}

    # Research salary for top 10 jobs max (to save credits)
    for job in missing_salary[:10]:
        query = (
            f"{job['title']} {job['company']} salary India LPA "
            f"fresher package Glassdoor AmbitionBox"
        )
        try:
            results = client.search(
                query=query,
                max_results=3,
                search_depth="basic",
            )
            combined_text = " ".join(
                r.get("content", "") for r in results.get("results", [])
            )
            salary_min, salary_max = extract_salary_from_text(combined_text)
            if salary_min:
                job["salary_min"] = salary_min
                job["salary_max"] = salary_max
                console.print(
                    f"[green]  💰 {job['company']} {job['title'][:30]}: "
                    f"₹{salary_min}–{salary_max} LPA[/green]"
                )
        except Exception as e:
            console.print(f"[red]Research error ({job['company']}): {e}[/red]")

    console.print(f"[green]✅ Research Agent done[/green]")
    return {**state, "enriched_jobs": filtered_jobs}

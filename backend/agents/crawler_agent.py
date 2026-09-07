import asyncio
from typing import List, Dict, Any
from backend.crawlers.registry import get_all_crawlers
from backend.crawlers.tavily_fallback import tavily_search_jobs
from backend.config import get_settings
from rich.console import Console

console = Console()
settings = get_settings()


async def run_crawler_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agent 1: Runs all registered crawlers in parallel.
    Falls back to Tavily for any crawler that returns 0 jobs.
    """
    console.print("\n[bold blue]═══ Agent 1: Crawler Agent ═══[/bold blue]")

    profile = state.get("profile", {})
    grad_year = profile.get("grad_year", "2025")
    preferred_roles = profile.get("preferred_roles", "SDE").split(",")

    crawlers = get_all_crawlers()

    # Run all crawlers concurrently
    tasks = [crawler.run() for crawler in crawlers]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_jobs: List[Dict[str, Any]] = []

    for crawler, result in zip(crawlers, results):
        if isinstance(result, Exception):
            console.print(f"[red]Crawler exception ({crawler.company_name}): {result}[/red]")
            result = []

        if len(result) == 0:
            # Fallback to Tavily for this company
            console.print(
                f"[yellow]⚠️  {crawler.company_name}: 0 jobs from crawler "
                f"→ trying Tavily fallback[/yellow]"
            )
            fallback_jobs = tavily_search_jobs(
                company=crawler.company_name,
                roles=preferred_roles,
                grad_year=grad_year,
                company_type=crawler.company_type,
                tavily_api_key=settings.tavily_api_key,
            )
            all_jobs.extend(fallback_jobs)
        else:
            all_jobs.extend(result)

    console.print(
        f"\n[green]✅ Crawler Agent done: {len(all_jobs)} raw jobs collected "
        f"from {len(crawlers)} companies[/green]"
    )

    return {**state, "raw_jobs": all_jobs}

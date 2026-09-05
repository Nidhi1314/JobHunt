from typing import List, Dict, Any
from rich.console import Console

console = Console()


def tavily_search_jobs(
    company: str,
    roles: List[str],
    grad_year: str,
    company_type: str = "",
    tavily_api_key: str = "",
) -> List[Dict[str, Any]]:
    """
    Fallback search via Tavily when Playwright crawler fails or is blocked.
    Uses ~2 credits per company (1 per role, max 2 roles).
    """
    if not tavily_api_key:
        console.print("[yellow]⚠️  Tavily key not set — skipping fallback[/yellow]")
        return []

    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=tavily_api_key)
    except ImportError:
        console.print("[red]tavily-python not installed[/red]")
        return []

    jobs = []
    for role in roles[:2]:  # max 2 roles to save credits
        query = (
            f"{company} {role} jobs India {grad_year} "
            f"new grad freshers entry level hiring 2025"
        )
        try:
            results = client.search(
                query=query,
                max_results=5,
                search_depth="basic",
            )
            for r in results.get("results", []):
                title = r.get("title", f"{role} at {company}")
                url = r.get("url", "")
                content = r.get("content", "")
                # Only include if it looks like a job listing
                if any(kw in content.lower() for kw in ["apply", "hiring", "job", "engineer", "analyst"]):
                    jobs.append({
                        "title": title,
                        "company": company,
                        "url": url,
                        "location": "India",
                        "work_mode": None,
                        "salary_min": None,
                        "salary_max": None,
                        "grad_year": grad_year,
                        "raw_description": content[:500],
                        "company_type": company_type,
                    })
        except Exception as e:
            console.print(f"[red]Tavily error ({company}/{role}): {e}[/red]")

    return jobs

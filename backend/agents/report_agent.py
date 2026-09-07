from typing import List, Dict, Any
from datetime import datetime
from sqlmodel import Session, select
from backend.db.database import engine, job_exists
from backend.models.schemas import Job
from rich.console import Console
from rich.table import Table

console = Console()


async def run_report_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agent 4: Deduplicates jobs against SQLite, saves new ones, prepares email payload.
    """
    console.print("\n[bold blue]═══ Agent 4: Report Agent ═══[/bold blue]")

    enriched_jobs: List[Dict[str, Any]] = state.get("enriched_jobs", [])

    if not enriched_jobs:
        console.print("[yellow]No jobs to report.[/yellow]")
        return {**state, "new_jobs": [], "email_ready": False}

    new_jobs = []

    with Session(engine) as session:
        for job_data in enriched_jobs:
            title = job_data.get("title", "")
            company = job_data.get("company", "")
            url = job_data.get("url", "")

            if not title or not url:
                continue

            seen_hash = Job.make_hash(title, company, url)

            # Skip duplicates
            if job_exists(session, seen_hash):
                continue

            # Save new job to DB
            new_job = Job(
                title=title,
                company=company,
                url=url,
                location=job_data.get("location"),
                work_mode=job_data.get("work_mode"),
                salary_min=job_data.get("salary_min"),
                salary_max=job_data.get("salary_max"),
                grad_year=job_data.get("grad_year"),
                company_type=job_data.get("company_type"),
                relevance_score=job_data.get("relevance_score"),
                raw_description=job_data.get("raw_description"),
                seen_hash=seen_hash,
                first_seen=datetime.utcnow(),
                emailed=False,
            )
            session.add(new_job)
            new_jobs.append(job_data)

        session.commit()

    # Print summary table
    if new_jobs:
        table = Table(title=f"🆕 New Jobs This Run ({len(new_jobs)})", show_lines=True)
        table.add_column("Score", style="yellow", width=6)
        table.add_column("Title", style="cyan", max_width=35)
        table.add_column("Company", style="green", width=12)
        table.add_column("Location", width=12)
        table.add_column("Salary (LPA)", width=12)

        for j in new_jobs[:15]:
            score = f"{j.get('relevance_score', 0):.1f}"
            sal_min = j.get("salary_min")
            sal_max = j.get("salary_max")
            salary = f"₹{sal_min}–{sal_max}" if sal_min else "Unknown"
            table.add_row(
                score,
                j["title"][:35],
                j.get("company", ""),
                j.get("location", "") or "",
                salary,
            )
        console.print(table)
    else:
        console.print("[cyan]No new jobs this run — all already seen.[/cyan]")

    console.print(
        f"\n[green]✅ Report Agent done: {len(new_jobs)} new jobs saved to DB[/green]"
    )

    return {
        **state,
        "new_jobs": new_jobs,
        "jobs_crawled": len(state.get("raw_jobs", [])),
        "jobs_after_filter": len(enriched_jobs),
        "jobs_new": len(new_jobs),
        "email_ready": len(new_jobs) > 0,
    }

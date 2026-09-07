"""
Test email sending with jobs from DB.
Usage: python test_email.py
"""
import asyncio
from sqlmodel import Session, select
from backend.db.database import engine
from backend.models.schemas import Job
from backend.email_sender.gmail_sender import send_job_alert_async
from rich.console import Console

console = Console()


async def main():
    with Session(engine) as session:
        jobs = session.exec(
            select(Job).order_by(Job.first_seen.desc()).limit(20)
        ).all()

    if not jobs:
        console.print("[red]No jobs in DB yet — run test_pipeline.py first[/red]")
        return

    job_dicts = [
        {
            "title": j.title,
            "company": j.company,
            "url": j.url,
            "location": j.location,
            "work_mode": j.work_mode,
            "salary_min": j.salary_min,
            "salary_max": j.salary_max,
            "company_type": j.company_type,
            "relevance_score": j.relevance_score or 6.0,
        }
        for j in jobs
    ]

    console.print(f"[cyan]Sending test email with {len(job_dicts)} jobs...[/cyan]")
    success = await send_job_alert_async(job_dicts)

    if success:
        console.print("[green]✅ Check your inbox![/green]")
    else:
        console.print("[red]Failed — check your .env keys (GMAIL_USER, GMAIL_APP_PASSWORD, ALERT_TO_EMAIL)[/red]")


if __name__ == "__main__":
    asyncio.run(main())

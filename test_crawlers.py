"""
Quick test — run a single crawler to verify it works.
Usage:  python test_crawlers.py
"""
import asyncio
from backend.crawlers.companies.google import GoogleCrawler
from rich.console import Console
from rich.table import Table

console = Console()


async def main():
    crawler = GoogleCrawler()
    jobs = await crawler.run()

    if not jobs:
        console.print("[red]No jobs found — crawler may be blocked or page changed[/red]")
        return

    table = Table(title=f"Google Jobs ({len(jobs)} found)")
    table.add_column("Title", style="cyan", max_width=50)
    table.add_column("Location", style="green")
    table.add_column("URL", style="blue", max_width=40)

    for job in jobs[:10]:
        table.add_row(job["title"], job["location"] or "-", job["url"][:40])

    console.print(table)


if __name__ == "__main__":
    asyncio.run(main())

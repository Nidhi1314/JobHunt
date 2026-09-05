from abc import ABC, abstractmethod
from typing import List, Dict, Any
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio
from rich.console import Console

console = Console()


class BaseCrawler(ABC):
    """Abstract base crawler using Playwright + BeautifulSoup."""

    company_name: str = ""
    careers_url: str = ""
    company_type: str = ""  # Product / MNC / Startup / Service

    def __init__(self, timeout: int = 30000):
        self.timeout = timeout  # milliseconds

    async def fetch_page(self, url: str, wait_selector: str = None) -> str:
        """Launch headless browser, load URL, return full HTML."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            )
            page = await context.new_page()
            html = ""
            try:
                await page.goto(url, timeout=self.timeout, wait_until="domcontentloaded")
                if wait_selector:
                    try:
                        await page.wait_for_selector(wait_selector, timeout=10000)
                    except Exception:
                        pass  # selector didn't appear, continue anyway
                else:
                    await asyncio.sleep(3)  # let JS render
                html = await page.content()
            except Exception as e:
                console.print(f"[red]Fetch error ({self.company_name}): {e}[/red]")
            finally:
                await browser.close()
        return html

    def parse(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, "lxml")

    def make_job(
        self,
        title: str,
        url: str,
        location: str = None,
        work_mode: str = None,
        salary_min: float = None,
        salary_max: float = None,
        grad_year: str = None,
        raw_description: str = None,
    ) -> Dict[str, Any]:
        """Build a standardized job dict."""
        return {
            "title": title.strip(),
            "company": self.company_name,
            "url": url.strip() if url else self.careers_url,
            "location": location,
            "work_mode": work_mode,
            "salary_min": salary_min,
            "salary_max": salary_max,
            "grad_year": grad_year,
            "raw_description": raw_description,
            "company_type": self.company_type,
        }

    @abstractmethod
    async def crawl(self) -> List[Dict[str, Any]]:
        """Override this in each company crawler."""
        pass

    async def run(self) -> List[Dict[str, Any]]:
        """Public entry point with logging + error handling."""
        try:
            console.print(f"[cyan]🕷️  Crawling {self.company_name}...[/cyan]")
            jobs = await self.crawl()
            console.print(
                f"[green]✅ {self.company_name}: {len(jobs)} jobs found[/green]"
            )
            return jobs
        except Exception as e:
            console.print(f"[red]❌ {self.company_name} crawler failed: {e}[/red]")
            return []

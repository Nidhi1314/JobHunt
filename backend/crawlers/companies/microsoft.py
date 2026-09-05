from typing import List, Dict, Any
from backend.crawlers.base_crawler import BaseCrawler


class MicrosoftCrawler(BaseCrawler):
    company_name = "Microsoft"
    careers_url = "https://jobs.careers.microsoft.com/global/en/search?q=software+engineer&lc=India&l=en_us&pgSz=20&o=Relevance&flt=true"
    company_type = "Product"

    async def crawl(self) -> List[Dict[str, Any]]:
        html = await self.fetch_page(self.careers_url, wait_selector="div[class*='ms-List']")
        soup = self.parse(html)
        jobs = []

        cards = (
            soup.select("div[class*='ms-List-cell']")
            or soup.select("[data-automationid='jobCard']")
            or soup.select("li[role='listitem']")
        )

        for card in cards[:20]:
            title_el = card.find(["h2", "h3", "a"])
            link_el = card.find("a", href=True)
            loc_el = card.find(string=lambda t: t and ("India" in t or "Hyderabad" in t or "Bangalore" in t) if t else False)

            if not title_el:
                continue

            url = link_el["href"] if link_el else self.careers_url
            if url.startswith("/"):
                url = f"https://jobs.careers.microsoft.com{url}"

            jobs.append(self.make_job(
                title=title_el.get_text(strip=True),
                url=url,
                location=str(loc_el).strip() if loc_el else "India",
                work_mode="Hybrid",
            ))

        return jobs

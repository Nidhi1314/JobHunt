from typing import List, Dict, Any
from backend.crawlers.base_crawler import BaseCrawler


class TCSCrawler(BaseCrawler):
    company_name = "TCS"
    careers_url = "https://ibegin.tcs.com/iBegin/jobs/search"
    company_type = "Service"

    async def crawl(self) -> List[Dict[str, Any]]:
        html = await self.fetch_page(self.careers_url)
        soup = self.parse(html)
        jobs = []

        cards = (
            soup.select("[class*='job']")
            or soup.select("[class*='position']")
            or soup.select("tr")
        )

        for card in cards[:20]:
            title_el = card.find(["h3", "h2", "td", "a", "strong"])
            link_el = card.find("a", href=True)

            if not title_el:
                continue

            title_text = title_el.get_text(strip=True)
            if len(title_text) < 3 or len(title_text) > 150:
                continue

            url = link_el["href"] if link_el else self.careers_url
            if url.startswith("/"):
                url = f"https://ibegin.tcs.com{url}"

            jobs.append(self.make_job(
                title=title_text,
                url=url,
                location="India",
                work_mode="On-site",
            ))

        return jobs

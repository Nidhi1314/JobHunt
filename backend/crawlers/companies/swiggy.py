from typing import List, Dict, Any
from backend.crawlers.base_crawler import BaseCrawler


class SwiggyCrawler(BaseCrawler):
    company_name = "Swiggy"
    careers_url = "https://careers.swiggy.com/#careers"
    company_type = "Product"

    async def crawl(self) -> List[Dict[str, Any]]:
        html = await self.fetch_page(self.careers_url)
        soup = self.parse(html)
        jobs = []

        cards = (
            soup.select("[class*='job']")
            or soup.select("[class*='position']")
            or soup.select("[class*='opening']")
        )

        for card in cards[:20]:
            title_el = card.find(["h3", "h2", "h4", "strong"])
            link_el = card.find("a", href=True)

            if not title_el:
                continue

            url = link_el["href"] if link_el else self.careers_url

            jobs.append(self.make_job(
                title=title_el.get_text(strip=True),
                url=url,
                location="Bangalore",
                work_mode="Hybrid",
            ))

        return jobs

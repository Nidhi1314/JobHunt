from typing import List, Dict, Any
from backend.crawlers.base_crawler import BaseCrawler


class GoogleCrawler(BaseCrawler):
    company_name = "Google"
    careers_url = "https://careers.google.com/jobs/results/?employment_type=FULL_TIME&location=India&q=engineer"
    company_type = "Product"

    async def crawl(self) -> List[Dict[str, Any]]:
        html = await self.fetch_page(self.careers_url)
        soup = self.parse(html)
        jobs = []

        # Try multiple selector patterns (Google updates their DOM)
        cards = (
            soup.select("li[class*='lLd3Je']")
            or soup.select("div[class*='job-result']")
            or soup.select("article")
        )

        for card in cards[:20]:
            title_el = card.find(["h3", "h2", "h4"])
            link_el = card.find("a", href=True)
            loc_el = card.find("span", class_=lambda c: c and "location" in c.lower() if c else False)

            if not title_el:
                continue

            url = link_el["href"] if link_el else self.careers_url
            if url.startswith("/"):
                url = f"https://careers.google.com{url}"

            jobs.append(self.make_job(
                title=title_el.get_text(strip=True),
                url=url,
                location=loc_el.get_text(strip=True) if loc_el else "India",
                work_mode="On-site",
            ))

        return jobs

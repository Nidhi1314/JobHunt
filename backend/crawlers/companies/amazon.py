from typing import List, Dict, Any
from backend.crawlers.base_crawler import BaseCrawler


class AmazonCrawler(BaseCrawler):
    company_name = "Amazon"
    careers_url = "https://www.amazon.jobs/en/search?base_query=software+engineer&loc_query=India&employment_type=FULL_TIME"
    company_type = "Product"

    async def crawl(self) -> List[Dict[str, Any]]:
        html = await self.fetch_page(self.careers_url)
        soup = self.parse(html)
        jobs = []

        cards = soup.select("div.job-tile") or soup.select("[data-job-id]") or soup.select(".job")

        for card in cards[:20]:
            title_el = card.find(["h3", "h2", "a"])
            link_el = card.find("a", href=True)
            loc_el = card.find(class_=lambda c: c and "location" in c.lower() if c else False)

            if not title_el:
                continue

            url = link_el["href"] if link_el else self.careers_url
            if url.startswith("/"):
                url = f"https://www.amazon.jobs{url}"

            jobs.append(self.make_job(
                title=title_el.get_text(strip=True),
                url=url,
                location=loc_el.get_text(strip=True) if loc_el else "India",
                work_mode="On-site",
            ))

        return jobs

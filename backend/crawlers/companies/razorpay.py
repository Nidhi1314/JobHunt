from typing import List, Dict, Any
from backend.crawlers.base_crawler import BaseCrawler


class RazorpayCrawler(BaseCrawler):
    company_name = "Razorpay"
    careers_url = "https://razorpay.com/jobs/"
    company_type = "Startup"

    async def crawl(self) -> List[Dict[str, Any]]:
        html = await self.fetch_page(self.careers_url)
        soup = self.parse(html)
        jobs = []

        cards = (
            soup.select("div.job-listing")
            or soup.select("[class*='job']")
            or soup.select("[class*='opening']")
        )

        for card in cards[:20]:
            title_el = card.find(["h3", "h2", "a", "strong"])
            link_el = card.find("a", href=True)
            loc_el = card.find(class_=lambda c: c and "location" in c.lower() if c else False)

            if not title_el:
                continue

            url = link_el["href"] if link_el else self.careers_url
            if url.startswith("/"):
                url = f"https://razorpay.com{url}"

            jobs.append(self.make_job(
                title=title_el.get_text(strip=True),
                url=url,
                location=loc_el.get_text(strip=True) if loc_el else "Bangalore",
                work_mode="Hybrid",
            ))

        return jobs

from typing import List, Dict, Any, Type
from backend.crawlers.base_crawler import BaseCrawler
from backend.crawlers.companies.google import GoogleCrawler
from backend.crawlers.companies.amazon import AmazonCrawler
from backend.crawlers.companies.microsoft import MicrosoftCrawler
from backend.crawlers.companies.flipkart import FlipkartCrawler
from backend.crawlers.companies.swiggy import SwiggyCrawler
from backend.crawlers.companies.zomato import ZomatoCrawler
from backend.crawlers.companies.razorpay import RazorpayCrawler
from backend.crawlers.companies.cred import CREDCrawler
from backend.crawlers.companies.tcs import TCSCrawler
from backend.crawlers.companies.infosys import InfosysCrawler

# All registered crawlers — add more here as you expand
CRAWLER_REGISTRY: List[Type[BaseCrawler]] = [
    GoogleCrawler,
    AmazonCrawler,
    MicrosoftCrawler,
    FlipkartCrawler,
    SwiggyCrawler,
    ZomatoCrawler,
    RazorpayCrawler,
    CREDCrawler,
    TCSCrawler,
    InfosysCrawler,
]


def get_all_crawlers() -> List[BaseCrawler]:
    """Instantiate all registered crawlers."""
    return [cls() for cls in CRAWLER_REGISTRY]

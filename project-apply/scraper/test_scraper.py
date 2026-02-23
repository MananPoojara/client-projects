import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.infrastructure.scrapers.base_scraper import BaseScraper
from src.infrastructure.scrapers.scraper_factory import ScraperFactory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestScraper(BaseScraper):
    """Test scraper for demonstration."""
    
    name = "test"
    board_id = "test"
    
    async def scrape(self, keywords: list[str], location: str = "") -> list[dict]:
        logger.info(f"Testing scraper with keywords: {keywords}")
        
        results = []
        for i, keyword in enumerate(keywords):
            job = self._create_job_record(
                job_board_id=f"test-{i}",
                title=f"Software Engineer - {keyword}",
                company="Test Company",
                source_url=f"https://example.com/job/{i}",
                location=location or "Remote",
                work_type="remote",
                skills=["python", "javascript", "react"]
            )
            results.append(job)
        
        logger.info(f"Created {len(results)} test jobs")
        return results


async def main():
    factory = ScraperFactory()
    factory.register("test", TestScraper)
    
    scraper = factory.get_scraper("test")
    
    jobs = await scraper.scrape(
        keywords=["python developer", "react developer"],
        location="Remote"
    )
    
    print(f"\nScraped {len(jobs)} jobs:")
    for job in jobs:
        print(f"  - {job['title']} at {job['company']}")
        print(f"    Skills: {job.get('skills', [])}")
        print(f"    URL: {job['source_url']}\n")


if __name__ == "__main__":
    asyncio.run(main())

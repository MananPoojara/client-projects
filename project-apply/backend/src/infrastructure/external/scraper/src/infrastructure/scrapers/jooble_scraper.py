import logging
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.infrastructure.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class JoobleScraper(BaseScraper):
    """Scraper for Jooble job board (free API)."""
    
    name = "jooble"
    board_id = "jooble"
    base_url = "https://jooble.org"
    
    def __init__(self):
        super().__init__(None)
        self.config = {
            "board_id": "jooble",
            "name": "Jooble",
            "base_url": "https://jooble.org",
            "throttle": {"delay_seconds": 2}
        }
    
    def scrape(self, keywords: list[str], location: str = "", **kwargs) -> list[dict]:
        import requests
        
        results = []
        
        for keyword in keywords:
            try:
                url = "https://jooble.org/api/"
                
                payload = {
                    "keywords": keyword,
                    "location": location,
                    "page": 1,
                    "results_per_page": 20
                }
                
                response = requests.post(url, json=payload, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    jobs = data.get("jobs", [])
                    
                    for job in jobs:
                        result = self._create_job_record(
                            job_board_id=job.get("id", ""),
                            title=job.get("title", ""),
                            company=job.get("company", ""),
                            source_url=job.get("link", ""),
                            location=job.get("location", ""),
                            description=job.get("snippet", ""),
                            short_description=job.get("snippet", "")[:200] if job.get("snippet") else "",
                            work_type="remote" if "remote" in job.get("location", "").lower() else "unknown",
                            job_type="full_time",
                            skills=self._extract_skills(job.get("snippet", "")),
                            posted_date=job.get("updated", ""),
                            application_url=job.get("link", "")
                        )
                        results.append(result)
                        
                        logger.info(f"Found: {job.get('title')} at {job.get('company')}")
                else:
                    logger.warning(f"Error: Status {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Error scraping {keyword}: {e}")
        
        return results


def main():
    import json
    
    print("=" * 70)
    print("JOOBLE SCRAPER TEST")
    print("=" * 70)
    
    scraper = JoobleScraper()
    
    keywords = ["python", "javascript"]
    location = "remote"
    
    print(f"\nSearching: {keywords[0]} - {location}")
    print("-" * 70)
    
    jobs = scraper.scrape(keywords, location)
    
    print(f"\nTOTAL: {len(jobs)} jobs")
    
    for i, job in enumerate(jobs[:5], 1):
        print(f"\n{i}. {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   URL: {job['application_url']}")
    
    output_path = Path(__file__).parent.parent / "test_data" / "jooble_jobs.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump({"jobs": jobs}, f, indent=2)
    
    print(f"\nSaved to: {output_path}")


if __name__ == "__main__":
    main()

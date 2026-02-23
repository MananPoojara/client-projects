import logging
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.infrastructure.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class RemotiveScraper(BaseScraper):
    """Scraper for Remotive job board (free API)."""
    
    name = "remotive"
    board_id = "remotive"
    base_url = "https://remotive.com"
    
    def __init__(self):
        super().__init__(None)
        self.config = {
            "board_id": "remotive",
            "name": "Remotive",
            "base_url": "https://remotive.com",
            "throttle": {"delay_seconds": 2}
        }
    
    def scrape(self, keywords: list[str], location: str = "", **kwargs) -> list[dict]:
        import requests
        
        results = []
        
        for keyword in keywords:
            try:
                url = f"https://remotive.com/api/remote-jobs?category=software-dev&search={keyword}"
                
                response = requests.get(url, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    jobs = data.get("jobs", [])
                    
                    for job in jobs:
                        result = self._create_job_record(
                            job_board_id=str(job.get("id", "")),
                            title=job.get("title", ""),
                            company=job.get("company_name", ""),
                            source_url=job.get("url", ""),
                            location=job.get("candidate_required_location", ""),
                            description=job.get("description", ""),
                            short_description=job.get("summary", ""),
                            work_type="remote" if job.get("remote", False) else "onsite",
                            job_type="full_time",
                            skills=self._extract_skills(job.get("description", "")),
                            posted_date=job.get("publication_date", ""),
                            application_url=job.get("url", "")
                        )
                        results.append(result)
                        
                        logger.info(f"Found: {job.get('title')} at {job.get('company_name')}")
                
            except Exception as e:
                logger.error(f"Error scraping {keyword}: {e}")
        
        return results


def main():
    import json
    
    print("=" * 70)
    print("REMOTIVE SCRAPER TEST - Fetching Live Jobs")
    print("=" * 70)
    
    scraper = RemotiveScraper()
    
    keywords = ["python", "javascript", "react"]
    
    print(f"\nSearching for: {', '.join(keywords)}")
    print("-" * 70)
    
    jobs = scraper.scrape(keywords)
    
    print("\n" + "=" * 70)
    print(f"TOTAL JOBS FOUND: {len(jobs)}")
    print("=" * 70)
    
    for i, job in enumerate(jobs[:10], 1):
        print(f"\n{i}. {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   Location: {job.get('location', 'Remote')}")
        print(f"   Skills: {', '.join(job.get('skills', [])[:5])}")
        print(f"   APPLY URL: {job['application_url']}")
    
    output_path = Path(__file__).parent.parent.parent / "test_data" / "scraped_jobs.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump({"jobs": jobs}, f, indent=2)
    
    print(f"\n\nSaved {len(jobs)} jobs to: {output_path}")


if __name__ == "__main__":
    main()

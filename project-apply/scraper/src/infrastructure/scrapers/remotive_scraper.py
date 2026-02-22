import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))

from src.infrastructure.scrapers.base_scraper import BaseScraper


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
    
    async def scrape(self, keywords: list[str], location: str = "") -> list[dict]:
        import aiohttp
        
        results = []
        
        for keyword in keywords:
            try:
                url = f"https://remotive.com/api/remote-jobs?category=software-dev&search={keyword}"
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                        if response.status == 200:
                            data = await response.json()
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
                                
                                print(f"  Found: {job.get('title')} at {job.get('company_name')}")
                                print(f"    URL: {job.get('url')}")
                        
            except Exception as e:
                print(f"Error scraping {keyword}: {e}")
        
        return results
    
    def _extract_skills(self, description: str) -> list[str]:
        common_skills = [
            "python", "javascript", "java", "typescript", "react", "node.js",
            "django", "flask", "postgresql", "mysql", "mongodb", "redis",
            "aws", "azure", "gcp", "docker", "kubernetes", "git",
            "rest api", "graphql", "machine learning", "tensorflow"
        ]
        
        if not description:
            return []
        
        text_lower = description.lower()
        found = [skill for skill in common_skills if skill in text_lower]
        return list(set(found))[:10]


async def main():
    print("=" * 70)
    print("REAL SCRAPER TEST - Fetching Live Jobs")
    print("=" * 70)
    
    scraper = RemotiveScraper()
    
    keywords = ["python", "javascript", "react"]
    
    print(f"\nSearching for: {', '.join(keywords)}")
    print("-" * 70)
    
    jobs = await scraper.scrape(keywords)
    
    print("\n" + "=" * 70)
    print(f"TOTAL JOBS FOUND: {len(jobs)}")
    print("=" * 70)
    
    for i, job in enumerate(jobs[:10], 1):
        print(f"\n{i}. {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   Location: {job.get('location', 'Remote')}")
        print(f"   Skills: {', '.join(job.get('skills', [])[:5])}")
        print(f"   APPLY URL: {job['application_url']}")
    
    output_path = Path(__file__).parent.parent.parent.parent / "test_data" / "scraped_jobs.json"
    with open(output_path, "w") as f:
        json.dump({"jobs": jobs}, f, indent=2)
    
    print(f"\n\nSaved {len(jobs)} jobs to: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())

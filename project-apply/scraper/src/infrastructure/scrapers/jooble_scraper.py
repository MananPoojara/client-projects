import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.infrastructure.scrapers.base_scraper import BaseScraper


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
    
    async def scrape(self, keywords: list[str], location: str = "") -> list[dict]:
        import aiohttp
        
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
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as response:
                        if response.status == 200:
                            data = await response.json()
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
                                
                                print(f"  Found: {job.get('title')} at {job.get('company')}")
                                print(f"    URL: {job.get('link')}")
                        else:
                            print(f"  Error: Status {response.status}")
                            
            except Exception as e:
                print(f"Error: {e}")
        
        return results
    
    def _extract_skills(self, text: str) -> list[str]:
        common_skills = [
            "python", "javascript", "java", "typescript", "react", "node.js",
            "django", "flask", "postgresql", "mysql", "mongodb", "redis",
            "aws", "azure", "gcp", "docker", "kubernetes", "git"
        ]
        
        if not text:
            return []
        
        text_lower = text.lower()
        found = [skill for skill in common_skills if skill in text_lower]
        return list(set(found))[:8]


async def main():
    print("=" * 70)
    print("JOOBLE SCRAPER TEST")
    print("=" * 70)
    
    scraper = JoobleScraper()
    
    keywords = ["python", "javascript"]
    location = "remote"
    
    print(f"\nSearching: {keywords[0]} - {location}")
    print("-" * 70)
    
    jobs = await scraper.scrape(keywords, location)
    
    print(f"\nTOTAL: {len(jobs)} jobs")
    
    for i, job in enumerate(jobs[:5], 1):
        print(f"\n{i}. {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   URL: {job['application_url']}")
    
    output_path = Path(__file__).parent.parent.parent / "test_data" / "jooble_jobs.json"
    with open(output_path, "w") as f:
        json.dump({"jobs": jobs}, f, indent=2)
    
    print(f"\nSaved to: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())

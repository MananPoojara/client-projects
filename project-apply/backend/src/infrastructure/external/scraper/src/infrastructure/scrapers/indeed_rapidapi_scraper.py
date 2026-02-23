import asyncio
import json
import re
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.infrastructure.scrapers.base_scraper import BaseScraper


class IndeedRapidAPIScraper(BaseScraper):
    """Scraper for Indeed using RapidAPI."""
    
    name = "indeed"
    board_id = "indeed"
    base_url = "https://indeed12.p.rapidapi.com"
    
    def __init__(self, api_key: str = None):
        super().__init__(None)
        self.config = {
            "board_id": "indeed",
            "name": "Indeed",
            "base_url": "https://indeed12.p.rapidapi.com",
            "throttle": {"delay_seconds": 2}
        }
        self.api_key = api_key or "YOUR_RAPIDAPI_KEY"
    
    async def scrape(self, keywords: list[str], location: str = "") -> list[dict]:
        import aiohttp
        
        results = []
        
        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "indeed12.p.rapidapi.com"
        }
        
        for keyword in keywords:
            try:
                url = f"https://indeed12.p.rapidapi.com/jobs/search"
                querystring = {
                    "query": keyword,
                    "locality": location or "us",
                    "start": "0"
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers, params=querystring, timeout=aiohttp.ClientTimeout(total=30)) as response:
                        if response.status == 200:
                            data = await response.json()
                            jobs = data.get("job", [])
                            
                            if not jobs:
                                print(f"  No jobs found for '{keyword}'")
                                continue
                            
                            for job in jobs:
                                try:
                                    title = job.get("title", "")
                                    company = job.get("company", "")
                                    job_url = f"https://www.indeed.com{job.get('url', '')}" if job.get('url') else ""
                                    
                                    if not job_url:
                                        job_id = job.get("jobkey", "")
                                        job_url = f"https://www.indeed.com/viewjob?jk={job_id}"
                                    
                                    location = job.get("locality", "")
                                    if not location:
                                        location = job.get("formattedLocation", "")
                                    
                                    summary = job.get("snippet", "")
                                    
                                    result = self._create_job_record(
                                        job_board_id=job.get("jobkey", ""),
                                        title=title,
                                        company=company,
                                        source_url=job_url,
                                        location=location,
                                        description=summary,
                                        short_description=summary[:200] if summary else "",
                                        work_type="remote" if "remote" in summary.lower() else "unknown",
                                        job_type=job.get("jobType", "full_time"),
                                        salary_min=None,
                                        salary_max=None,
                                        salary_currency=None,
                                        skills=self._extract_skills(summary),
                                        posted_date=job.get("date", ""),
                                        application_url=job_url
                                    )
                                    results.append(result)
                                    
                                    print(f"  Found: {title[:40]} at {company[:20]}")
                                    print(f"    URL: {job_url[:60]}...")
                                    
                                except Exception as e:
                                    print(f"  Error parsing job: {e}")
                                    continue
                                    
                        elif response.status == 403:
                            print(f"  ERROR: API key invalid or quota exceeded")
                        elif response.status == 429:
                            print(f"  ERROR: Rate limited - wait before retrying")
                        else:
                            print(f"  Error: Status {response.status}")
                            
            except Exception as e:
                print(f"Error scraping Indeed: {e}")
        
        return results
    
    def _extract_skills(self, text: str) -> list[str]:
        common_skills = [
            "python", "javascript", "java", "typescript", "react", "node.js",
            "django", "flask", "postgresql", "mysql", "mongodb", "redis",
            "aws", "azure", "gcp", "docker", "kubernetes", "git",
            "rest api", "graphql", "machine learning", "tensorflow"
        ]
        
        if not text:
            return []
        
        text_lower = text.lower()
        found = [skill for skill in common_skills if skill in text_lower]
        return list(set(found))[:8]


async def main():
    print("=" * 70)
    print("INDEED SCRAPER (RapidAPI)")
    print("=" * 70)
    print("\nGet API key from: https://rapidapi.com/indeed12")
    print("Free tier available!")
    print("-" * 70)
    
    import os
    api_key = os.environ.get("RAPIDAPI_KEY", "")
    
    if not api_key:
        print("\nNo API key found. Set RAPIDAPI_KEY environment variable.")
        print("Example: set RAPIDAPI_KEY=your_api_key")
        print("\nTrying demo mode...")
    
    scraper = IndeedRapidAPIScraper(api_key=api_key)
    
    keywords = ["python developer"]
    location = "us"
    
    print(f"\nSearching: {keywords[0]}")
    print("-" * 70)
    
    jobs = await scraper.scrape(keywords, location)
    
    print(f"\nTOTAL: {len(jobs)} jobs")
    
    for i, job in enumerate(jobs[:5], 1):
        print(f"\n{i}. {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   Location: {job.get('location', 'N/A')}")
        print(f"   URL: {job['application_url']}")
    
    if jobs:
        output_path = Path(__file__).parent.parent.parent / "test_data" / "indeed_jobs.json"
        with open(output_path, "w") as f:
            json.dump({"jobs": jobs}, f, indent=2)
        print(f"\nSaved to: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())

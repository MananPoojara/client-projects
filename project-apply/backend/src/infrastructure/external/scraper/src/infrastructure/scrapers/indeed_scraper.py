import asyncio
import json
import re
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.infrastructure.scrapers.base_scraper import BaseScraper


class IndeedScraper(BaseScraper):
    """Scraper for Indeed job board."""
    
    name = "indeed"
    board_id = "indeed"
    base_url = "https://www.indeed.com"
    
    def __init__(self):
        super().__init__(None)
        self.config = {
            "board_id": "indeed",
            "name": "Indeed",
            "base_url": "https://www.indeed.com",
            "throttle": {"delay_seconds": 2}
        }
    
    async def scrape(self, keywords: list[str], location: str = "") -> list[dict]:
        import aiohttp
        from bs4 import BeautifulSoup
        
        results = []
        
        for keyword in keywords:
            try:
                search_url = f"https://www.indeed.com/jobs?q={keyword.replace(' ', '+')}&l={location.replace(' ', '+') if location else ''}"
                
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(search_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')
                            
                            job_cards = soup.select('.jobsearch-ResultsList > li')
                            
                            for card in job_cards:
                                try:
                                    title_elem = card.select_one('.jobtitle')
                                    if not title_elem:
                                        continue
                                    
                                    title = title_elem.get_text(strip=True)
                                    title_link = title_elem.find('a')
                                    job_url = "https://www.indeed.com" + title_link['href'] if title_link and title_link.get('href') else search_url
                                    
                                    company_elem = card.select_one('.company')
                                    company = company_elem.get_text(strip=True) if company_elem else "N/A"
                                    
                                    location_elem = card.select_one('.location')
                                    location = location_elem.get_text(strip=True) if location_elem else location or "Remote"
                                    
                                    summary_elem = card.select_one('.summary')
                                    summary = summary_elem.get_text(strip=True) if summary_elem else ""
                                    
                                    salary_elem = card.select_one('.salaryText')
                                    salary_text = salary_elem.get_text(strip=True) if salary_elem else ""
                                    salary_min, salary_max, currency = self._parse_salary(salary_text)
                                    
                                    job_id_elem = card.get('data-jk')
                                    job_id = job_id_elem if job_id_elem else ""
                                    
                                    result = self._create_job_record(
                                        job_board_id=job_id,
                                        title=title,
                                        company=company,
                                        source_url=job_url,
                                        location=location,
                                        description=summary,
                                        short_description=summary[:200] if summary else "",
                                        work_type="remote" if "remote" in summary.lower() else "unknown",
                                        job_type="full_time",
                                        salary_min=salary_min,
                                        salary_max=salary_max,
                                        salary_currency=currency,
                                        skills=self._extract_skills(summary),
                                        posted_date="",
                                        application_url=job_url
                                    )
                                    results.append(result)
                                    
                                    print(f"  Found: {title} at {company}")
                                    print(f"    URL: {job_url}")
                                    
                                except Exception as e:
                                    print(f"  Error parsing card: {e}")
                                    continue
                                    
                        else:
                            print(f"  Error: Status {response.status}")
                            
            except Exception as e:
                print(f"Error scraping Indeed for '{keyword}': {e}")
        
        return results
    
    def _parse_salary(self, salary_text: str) -> tuple:
        if not salary_text:
            return None, None, None
        
        currency = "USD"
        numbers = re.findall(r'[\d,]+', salary_text.replace('$', '').replace(',', ''))
        numbers = [int(n) for n in numbers if n]
        
        if len(numbers) >= 2:
            return min(numbers), max(numbers), currency
        elif len(numbers) == 1:
            return numbers[0], numbers[0], currency
        
        return None, None, None
    
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
    print("INDEED SCRAPER TEST")
    print("=" * 70)
    
    scraper = IndeedScraper()
    
    keywords = ["python developer", "javascript developer"]
    location = "remote"
    
    print(f"\nSearching for: {', '.join(keywords)} in {location}")
    print("-" * 70)
    
    jobs = await scraper.scrape(keywords, location)
    
    print("\n" + "=" * 70)
    print(f"TOTAL JOBS FOUND: {len(jobs)}")
    print("=" * 70)
    
    for i, job in enumerate(jobs[:10], 1):
        print(f"\n{i}. {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   Location: {job.get('location', 'N/A')}")
        print(f"   Skills: {', '.join(job.get('skills', [])[:5])}")
        print(f"   APPLY URL: {job['application_url']}")
    
    output_path = Path(__file__).parent.parent.parent / "test_data" / "indeed_jobs.json"
    with open(output_path, "w") as f:
        json.dump({"jobs": jobs}, f, indent=2)
    
    print(f"\n\nSaved {len(jobs)} jobs to: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())

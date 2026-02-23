import asyncio
import json
import re
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.infrastructure.scrapers.base_scraper import BaseScraper


class IndeedScraperPlaywright(BaseScraper):
    """Indeed scraper using Playwright (headless browser)."""
    
    name = "indeed"
    board_id = "indeed"
    base_url = "https://www.indeed.com"
    
    def __init__(self):
        super().__init__(None)
        self.config = {
            "board_id": "indeed",
            "name": "Indeed",
            "base_url": "https://www.indeed.com",
            "throttle": {"delay_seconds": 3}
        }
    
    async def scrape(self, keywords: list[str], location: str = "") -> list[dict]:
        from playwright.async_api import async_playwright
        
        results = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = await context.new_page()
            
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            for keyword in keywords:
                try:
                    search_url = f"https://www.indeed.com/jobs?q={keyword.replace(' ', '+')}&l={location.replace(' ', '+') if location else ''}"
                    
                    print(f"  Loading: {search_url}")
                    await page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
                    await asyncio.sleep(3)
                    
                    job_cards = await page.query_selector_all('.jobsearch-ResultsList > li')
                    print(f"  Found {len(job_cards)} job cards")
                    
                    for card in job_cards[:15]:
                        try:
                            title_elem = await card.query_selector('.jobtitle')
                            if not title_elem:
                                continue
                            
                            title = await title_elem.inner_text()
                            title_link = await title_elem.query_selector('a')
                            job_url = ""
                            if title_link:
                                href = await title_link.get_attribute('href')
                                job_url = f"https://www.indeed.com{href}" if href else search_url
                            else:
                                job_url = search_url
                            
                            company_elem = await card.query_selector('.company')
                            company = await company_elem.inner_text() if company_elem else "N/A"
                            
                            location_elem = await card.query_selector('.location')
                            location_val = await location_elem.inner_text() if location_elem else location or "N/A"
                            
                            summary_elem = await card.query_selector('.summary')
                            summary = await summary_elem.inner_text() if summary_elem else ""
                            
                            job_id = await card.get_attribute('data-jk') or ""
                            
                            result = self._create_job_record(
                                job_board_id=job_id,
                                title=title,
                                company=company.strip(),
                                source_url=job_url,
                                location=location_val.strip(),
                                description=summary.strip(),
                                short_description=summary.strip()[:200] if summary else "",
                                work_type="remote" if "remote" in summary.lower() else "unknown",
                                job_type="full_time",
                                skills=self._extract_skills(summary),
                                posted_date="",
                                application_url=job_url
                            )
                            results.append(result)
                            
                            print(f"    - {title[:40]} at {company[:20]}")
                            print(f"      URL: {job_url[:60]}...")
                            
                        except Exception as e:
                            print(f"    Error: {e}")
                            continue
                            
                except Exception as e:
                    print(f"  Error: {e}")
                
                await asyncio.sleep(2)
            
            await browser.close()
        
        return results
    
    def _extract_skills(self, text: str) -> list[str]:
        common_skills = [
            "python", "javascript", "java", "typescript", "react", "node.js",
            "django", "flask", "postgresql", "mysql", "mongodb", "redis",
            "aws", "azure", "gcp", "docker", "kubernetes", "git",
            "rest api", "graphql", "machine learning"
        ]
        
        if not text:
            return []
        
        text_lower = text.lower()
        found = [skill for skill in common_skills if skill in text_lower]
        return list(set(found))[:8]


async def main():
    print("=" * 70)
    print("INDEED SCRAPER (Playwright)")
    print("=" * 70)
    
    scraper = IndeedScraperPlaywright()
    
    keywords = ["python developer"]
    location = "remote"
    
    print(f"\nSearching: {keywords[0]} in {location}")
    print("-" * 70)
    
    jobs = await scraper.scrape(keywords, location)
    
    print(f"\nTOTAL: {len(jobs)} jobs")
    
    for i, job in enumerate(jobs[:5], 1):
        print(f"\n{i}. {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   URL: {job['application_url']}")
    
    output_path = Path(__file__).parent.parent.parent / "test_data" / "indeed_jobs.json"
    with open(output_path, "w") as f:
        json.dump({"jobs": jobs}, f, indent=2)
    
    print(f"\nSaved to: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())

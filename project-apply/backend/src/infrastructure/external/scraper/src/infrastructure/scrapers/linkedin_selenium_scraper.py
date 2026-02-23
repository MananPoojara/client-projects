import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.infrastructure.scrapers.base_scraper import BaseScraper


class LinkedInSeleniumScraper(BaseScraper):
    """LinkedIn scraper using Selenium with stealth mode."""
    
    name = "linkedin"
    board_id = "linkedin"
    base_url = "https://www.linkedin.com"
    
    def __init__(self):
        super().__init__(None)
        self.config = {
            "board_id": "linkedin",
            "name": "LinkedIn",
            "base_url": "https://www.linkedin.com",
            "throttle": {"delay_seconds": 3}
        }
        self.driver = None
        self.results = []
    
    def _configure_webdriver(self):
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service as ChromeService
        from selenium.webdriver.common.by import By
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium_stealth import stealth
        
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()), 
            options=options
        )
        
        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
        )
        
        return driver
    
    def scrape(self, keywords: list[str], location: str = "") -> list[dict]:
        from bs4 import BeautifulSoup
        
        self.driver = self._configure_webdriver()
        self.results = []
        
        for keyword in keywords:
            try:
                search_url = f"https://www.linkedin.com/jobs/search/?keywords={keyword.replace(' ', '%20')}"
                if location:
                    search_url += f"&location={location.replace(' ', '%20')}"
                
                print(f"  Searching: {search_url}")
                self.driver.get(search_url)
                
                import time
                time.sleep(5)
                
                soup = BeautifulSoup(self.driver.page_source, 'lxml')
                
                job_cards = soup.find_all('div', class_='job-card-container')
                
                if not job_cards:
                    job_cards = soup.find_all('li', class_='jobs-search-results__list-item')
                
                print(f"  Found {len(job_cards)} jobs")
                
                for card in job_cards[:15]:
                    try:
                        title_elem = card.find('h3', class_='job-card-list__title')
                        if not title_elem:
                            title_elem = card.find('a', class_='job-card-list__title')
                        title = title_elem.text.strip() if title_elem else ""
                        
                        link_elem = card.find('a', class_='job-card-list__title')
                        job_url = ""
                        if link_elem:
                            href = link_elem.get('href', '')
                            job_url = href if href.startswith('http') else f"https://www.linkedin.com{href}"
                        
                        company_elem = card.find('h4', class_='job-card-container__company-name')
                        if not company_elem:
                            company_elem = card.find('span', class_='job-card-container__company-name')
                        company = company_elem.text.strip() if company_elem else ""
                        
                        location_elem = card.find('span', class_='job-card-container__metadata-item')
                        job_location = location_elem.text.strip() if location_elem else location
                        
                        result = self._create_job_record(
                            job_board_id="",
                            title=title,
                            company=company,
                            source_url=job_url,
                            location=job_location,
                            description="",
                            short_description="",
                            work_type="unknown",
                            job_type="full_time",
                            skills=[],
                            posted_date="",
                            application_url=job_url
                        )
                        
                        self.results.append(result)
                        print(f"    - {title[:40]} at {company[:20]}")
                        
                    except Exception as e:
                        print(f"    Error: {e}")
                        continue
                        
            except Exception as e:
                print(f"  Error: {e}")
        
        if self.driver:
            self.driver.quit()
        
        return self.results


def main():
    print("=" * 70)
    print("LINKEDIN SCRAPER (Selenium + Stealth)")
    print("=" * 70)
    
    scraper = LinkedInSeleniumScraper()
    
    keywords = ["python developer", "web developer"]
    location = "Remote"
    
    print(f"\nSearching: {', '.join(keywords)} in {location}")
    print("-" * 70)
    
    jobs = scraper.scrape(keywords, location)
    
    print(f"\nTOTAL: {len(jobs)} jobs")
    
    for i, job in enumerate(jobs[:10], 1):
        print(f"\n{i}. {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   Location: {job.get('location', 'N/A')}")
        print(f"   URL: {job['application_url']}")
    
    if jobs:
        output_path = Path(__file__).parent.parent.parent / "test_data" / "linkedin_jobs.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump({"jobs": jobs}, f, indent=2)
        print(f"\nSaved to: {output_path}")


if __name__ == "__main__":
    main()

import logging
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.infrastructure.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class IndeedSeleniumScraper(BaseScraper):
    """Indeed scraper using Selenium with stealth mode."""
    
    name = "indeed"
    board_id = "indeed"
    base_url = "https://www.indeed.com"
    
    COUNTRIES = {
        "us": "https://www.indeed.com",
        "uk": "https://uk.indeed.com",
        "ca": "https://ca.indeed.com",
        "in": "https://www.indeed.co.in",
        "au": "https://au.indeed.com",
        "de": "https://de.indeed.com",
        "fr": "https://www.indeed.fr",
    }
    
    def __init__(self):
        super().__init__(None)
        self.config = {
            "board_id": "indeed",
            "name": "Indeed",
            "base_url": "https://www.indeed.com",
            "throttle": {"delay_seconds": 2}
        }
        self.driver = None
        self.results = []
    
    def _configure_webdriver(self):
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service as ChromeService
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium_stealth import stealth
        
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("start-maximized")
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
    
    def scrape(self, keywords: list[str], location: str = "", country: str = "us", date_posted: int = 7, **kwargs) -> list[dict]:
        from bs4 import BeautifulSoup
        from selenium.common.exceptions import NoSuchElementException
        
        self.driver = self._configure_webdriver()
        self.results = []
        
        base_url = self.COUNTRIES.get(country, self.COUNTRIES["us"])
        
        for keyword in keywords:
            try:
                full_url = f"{base_url}/jobs?q={'+'.join(keyword.split())}&l={location}&fromage={date_posted}"
                logger.info(f"Searching: {full_url}")
                
                self.driver.get(full_url)
                
                try:
                    job_count_element = self.driver.find_element(
                        "xpath", 
                        '//div[starts-with(@class, "jobsearch-JobCountAndSortPane-jobCount")]'
                    )
                    total_jobs = job_count_element.find_element("xpath", './span').text
                    logger.info(f"Found: {total_jobs} jobs")
                except NoSuchElementException:
                    total_jobs = "Unknown"
                    logger.warning("Could not get job count")
                
                page_count = 0
                while True:
                    page_count += 1
                    logger.info(f"Page {page_count}...")
                    
                    soup = BeautifulSoup(self.driver.page_source, 'lxml')
                    boxes = soup.find_all('div', class_='job_seen_beacon')
                    
                    if not boxes:
                        logger.warning("No jobs found on page")
                        break
                    
                    for box in boxes:
                        try:
                            link = box.find('a', {'data-jk': True})
                            if link:
                                link_full = base_url + link.get('href')
                            else:
                                link = box.find('a', class_='JobTitle')
                                link_full = base_url + link.get('href') if link else ""
                            
                            title_elem = box.find('a', class_='JobTitle')
                            title = title_elem.text.strip() if title_elem else ""
                            
                            company_elem = box.find('span', {'data-testid': 'company-name'})
                            company = company_elem.text.strip() if company_elem else ""
                            
                            location_elem = box.find('div', {'data-testid': 'text-location'})
                            if location_elem:
                                loc_span = location_elem.find('span')
                                job_location = loc_span.text.strip() if loc_span else location_elem.text.strip()
                            else:
                                job_location = location
                            
                            try:
                                employer_active = box.find('span', class_='date').text.strip()
                            except:
                                employer_active = ""
                            
                            job_data = self._create_job_record(
                                job_board_id=link.get('data-jk') if link else "",
                                title=title,
                                company=company,
                                source_url=link_full,
                                location=job_location,
                                description=employer_active,
                                short_description=employer_active[:200] if employer_active else "",
                                work_type="remote" if "remote" in job_location.lower() else "unknown",
                                job_type="full_time",
                                skills=self._extract_skills(employer_active),
                                posted_date=employer_active,
                                application_url=link_full
                            )
                            
                            self.results.append(job_data)
                            logger.info(f"- {title[:40]} at {company[:20]}")
                            
                        except Exception as e:
                            logger.error(f"Error parsing job: {e}")
                            continue
                    
                    try:
                        next_page = soup.find('a', {'aria-label': 'Next Page'})
                        if next_page:
                            next_url = base_url + next_page.get('href')
                            self.driver.get(next_url)
                        else:
                            break
                    except:
                        break
                        
            except Exception as e:
                logger.error(f"Error: {e}")
        
        if self.driver:
            self.driver.quit()
        
        return self.results


def main():
    import json
    
    print("=" * 70)
    print("INDEED SCRAPER (Selenium + Stealth)")
    print("=" * 70)
    
    scraper = IndeedSeleniumScraper()
    
    keywords = ["python developer", "web developer"]
    location = "remote"
    country = "us"
    date_posted = 7
    
    print(f"\nSearching: {', '.join(keywords)} in {location}")
    print("-" * 70)
    
    jobs = scraper.scrape(keywords, location, country, date_posted)
    
    print(f"\n{'=' * 70}")
    print(f"TOTAL: {len(jobs)} jobs")
    print("=" * 70)
    
    for i, job in enumerate(jobs[:10], 1):
        print(f"\n{i}. {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   Location: {job.get('location', 'N/A')}")
        print(f"   URL: {job['application_url']}")
    
    if jobs:
        output_path = Path(__file__).parent.parent.parent / "test_data" / "indeed_jobs.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump({"jobs": jobs}, f, indent=2)
        print(f"\nSaved to: {output_path}")


if __name__ == "__main__":
    main()

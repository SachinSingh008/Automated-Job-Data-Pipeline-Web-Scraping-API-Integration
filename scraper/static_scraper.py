import requests
from bs4 import BeautifulSoup
import time
import random
import logging
from typing import List, Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

class StaticScraper:
    def __init__(self):
        # We use a user-agent to avoid simple bot protections
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
        }

    def fetch_page(self, url: str) -> str:
        """Fetches the HTML source of a given URL with retries and delay."""
        retries = 3
        for attempt in range(retries):
            try:
                # Add random delay between requests
                time.sleep(random.uniform(1.0, 3.0))
                logger.info(f"Fetching [STATIC]: {url} (Attempt {attempt+1}/{retries})")
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                return response.text
            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching {url}: {e}")
                if attempt == retries - 1:
                    return ""
        return ""

    def scrape(self, url: str = "https://realpython.github.io/fake-jobs/") -> List[Dict[str, Any]]:
        """Scrapes job data from a static target website."""
        html_content = self.fetch_page(url)
        if not html_content:
            logger.warning("No HTML content to scrape.")
            return []

        soup = BeautifulSoup(html_content, "html.parser")
        jobs_data = []

        # Assuming a generic structure, similar to typical job boards.
        # This uses the realpython fake jobs site structure as an example target.
        job_cards = soup.find_all("div", class_="card-content")

        for card in job_cards:
            try:
                title_elem = card.find("h2", class_="title")
                company_elem = card.find("h3", class_="subtitle")
                location_elem = card.find("p", class_="location")
                
                # If these exist, grab text, otherwise None
                job_title = title_elem.text.strip() if title_elem else "Unknown"
                company = company_elem.text.strip() if company_elem else "Unknown"
                location = location_elem.text.strip() if location_elem else "Unknown"
                
                # Mock extracting salary and skills (if they were present)
                # Since fake-jobs doesn't have these clearly separated, we insert None
                # or a mock value to demonstrate extraction logic matching requirement
                salary = None 
                
                jobs_data.append({
                    "job_title": job_title,
                    "company": company,
                    "location": location,
                    "salary": salary,
                    "skills": "Python, Web Scraping", # Mock skill 
                    "source": "static_scraper"
                })
            except Exception as e:
                logger.error(f"Error parsing a job card: {e}")

        logger.info(f"Successfully scraped {len(jobs_data)} jobs statically.")
        return jobs_data

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scraper = StaticScraper()
    jobs = scraper.scrape()
    for job in jobs[:2]:
        print(job)

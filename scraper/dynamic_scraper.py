from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class DynamicScraper:
    def __init__(self):
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--window-size=1920,1080")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36")
        
    def setup_driver(self):
        # We assume Chrome/ChromeDriver is installed and in PATH
        # For a robust setup we might use webdriver_manager, but standard Selenium works
        # if chromedriver is available.
        return webdriver.Chrome(options=self.options)

    def scrape(self, url: str = "https://news.ycombinator.com/jobs") -> List[Dict[str, Any]]:
        """Scrapes a dynamic or JS-heavy website using Selenium."""
        driver = None
        jobs_data = []
        try:
            driver = self.setup_driver()
            logger.info(f"Fetching [DYNAMIC]: {url}")
            driver.get(url)
            
            # Add implicit wait for elements to load
            driver.implicitly_wait(5)
            
            # Example logic for infinite scroll / pagination:
            # Let's scroll down once to demonstrate infinite scroll handling
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2.0, 4.0)) # Random delay
            
            # For demonstration, we target Hacker News Jobs layout
            # which is just simple TR elements with class 'athing'
            job_rows = driver.find_elements(By.CLASS_NAME, "athing")
            
            for row in job_rows:
                try:
                    title_elem = row.find_element(By.CLASS_NAME, "titleline")
                    job_title = title_elem.text.strip() if title_elem else "Unknown"
                    
                    # Hacker News Jobs doesn't typically have structured company/location
                    # We will mock partial extraction for the required fields
                    
                    jobs_data.append({
                        "job_title": job_title,
                        "company": "Startup",          # Default mock
                        "location": "Remote",          # Default mock
                        "salary": "$100k-$150k",       # Mock
                        "skills": "Python, React",     # Mock
                        "source": "dynamic_scraper"
                    })
                except Exception as e:
                    logger.warning(f"Failed to parse a dynamic job row: {e}")
            
        except Exception as e:
            logger.error(f"Error during dynamic scraping: {e}")
        finally:
            if driver:
                driver.quit()
        
        logger.info(f"Successfully scraped {len(jobs_data)} jobs dynamically.")
        return jobs_data

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scraper = DynamicScraper()
    jobs = scraper.scrape()
    for job in jobs[:2]:
        print(job)

import requests
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class WellfoundScraper:
    """
    Scraper module for Wellfound (formerly AngelList Talent).
    Designed to fetch jobs if accessible, or log errors (such as 403 Forbidden)
    and return an empty list to skip Wellfound gracefully.
    """
    
    TARGET_URL = "https://wellfound.com/jobs"
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }

    def fetch_jobs(self) -> list:
        """
        Attempts to scrape Wellfound jobs. If blocked (403/Forbidden) or error occurs,
        logs the error, returns an empty list, and continues execution.
        """
        logger.info(f"Attempting to connect to Wellfound: {self.TARGET_URL}")
        try:
            response = requests.get(self.TARGET_URL, headers=self.headers, timeout=10)
            if response.status_code == 403:
                logger.error("Wellfound returned HTTP 403 Forbidden (Cloudflare protection active). Skipping Wellfound ingestion.")
                return []
            elif response.status_code != 200:
                logger.error(f"Wellfound returned unexpected status code {response.status_code}. Skipping Wellfound ingestion.")
                return []
                
            logger.info("Successfully reached Wellfound page! Parsing HTML...")
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Placeholder for parsing logic. If it works, look for cards and fields.
            # e.g., cards = soup.find_all(...)
            # For now, if no listings match or if blocked on inner elements:
            logger.warning("No jobs could be parsed from the Wellfound page layout.")
            return []
            
        except Exception as e:
            logger.error(f"Error connecting to or parsing Wellfound: {e}")
            return []

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scraper = WellfoundScraper()
    jobs = scraper.fetch_jobs()
    print(f"Scraped {len(jobs)} jobs from Wellfound.")


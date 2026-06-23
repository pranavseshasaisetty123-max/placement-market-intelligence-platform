import requests
from bs4 import BeautifulSoup
import logging
import time
import re
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class InternshalaScraper:
    """
    Scraper module for extracting job listings from Internshala.
    Implements pagination, rate limiting, and robust HTML extraction.
    """
    
    BASE_URL = "https://internshala.com/jobs/page-{page}/"
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }

    def fetch_jobs(self, max_pages: int = 3, rate_limit_delay: float = 2.0) -> list:
        """
        Loops through pages of Internshala job search results, parses HTML,
        and returns a list of standardized job postings.
        """
        all_jobs = []
        
        for page in range(1, max_pages + 1):
            url = self.BASE_URL.format(page=page)
            logger.info(f"Scraping Internshala page {page}: {url}")
            
            try:
                response = requests.get(url, headers=self.headers, timeout=15)
                if response.status_code != 200:
                    logger.error(f"Internshala returned status code {response.status_code} for page {page}")
                    break
                
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('div', class_='individual_internship')
                
                if not job_cards:
                    logger.info(f"No job cards found on page {page}. Ending pagination.")
                    break
                
                logger.info(f"Found {len(job_cards)} job cards on page {page}.")
                
                for card in job_cards:
                    job = self._parse_card(card)
                    if job:
                        all_jobs.append(job)
                
                # Apply rate limit delay between pages
                if page < max_pages:
                    logger.info(f"Sleeping for {rate_limit_delay} seconds...")
                    time.sleep(rate_limit_delay)
                    
            except Exception as e:
                logger.error(f"Error scraping page {page}: {e}", exc_info=True)
                break
                
        logger.info(f"Successfully scraped {len(all_jobs)} jobs from Internshala.")
        return all_jobs

    def _parse_card(self, card) -> dict:
        """
        Parses a single individual_internship card and extracts job metadata.
        """
        try:
            # 1. Title & URL
            title_elem = card.find('a', class_='job-title-href')
            if not title_elem:
                return None
            title = title_elem.text.strip()
            job_url = "https://internshala.com" + title_elem.get('href', '').split('?')[0]
            
            # 2. Company Name
            company_elem = card.find(class_='company-name')
            company = company_elem.text.strip() if company_elem else "Unknown Company"
            
            # 3. Locations
            loc_elem = card.find(class_='locations')
            location = "Remote"
            if loc_elem:
                span_elem = loc_elem.find('span')
                if span_elem:
                    location = span_elem.text.strip()
            
            # 4. Salary/CTC
            # Find the row item containing money icon
            salary_str = "Not Specified"
            sal_min = None
            sal_max = None
            sal_currency = "INR"
            sal_period = "yearly"
            
            row_items = card.find_all('div', class_='row-1-item')
            for item in row_items:
                if item.find('i', class_='ic-16-money'):
                    # Found salary div
                    span_desc = item.find('span', class_='desktop')
                    if not span_desc:
                        span_desc = item.find('span')
                    if span_desc:
                        salary_str = span_desc.text.strip()
                        # Extract salary numbers
                        sal_min, sal_max = self._parse_salary_range(salary_str)
                        if "month" in salary_str.lower():
                            sal_period = "monthly"
            
            # 5. Experience level
            experience_str = "No experience required"
            for item in row_items:
                if item.find('i', class_='ic-16-briefcase'):
                    span_desc = item.find('span')
                    if span_desc:
                        experience_str = span_desc.text.strip()
            
            # 6. Posted Date
            # Look for status-inactive or status-active labels (e.g. "2 weeks ago")
            posted_date_str = "Just now"
            status_div = card.find(class_=lambda x: x and ('status-inactive' in x or 'status-active' in x or 'color-labels' in x))
            if status_div:
                span_desc = status_div.find('span')
                if span_desc:
                    posted_date_str = span_desc.text.strip()
            
            posted_date = self._parse_relative_date(posted_date_str)
            
            # 7. Job Description
            desc_div = card.find('div', class_='about_job')
            description = ""
            if desc_div:
                text_div = desc_div.find('div', class_='text')
                if text_div:
                    description = text_div.text.strip()
            if not description:
                description = f"Job listing for {title} at {company} in {location}."
                
            return {
                "job_title": title,
                "company_name": company,
                "location": location,
                "experience_level": experience_str,
                "salary": salary_str,
                "job_url": job_url,
                "source_platform": "Internshala",
                "source_portal": "Internshala", # compatibility field
                "posted_date": posted_date,
                "job_description": description,
                "raw_job_description": description, # compatibility field
                "salary_min": sal_min,
                "salary_max": sal_max,
                "salary_currency": sal_currency,
                "salary_period": sal_period
            }
            
        except Exception as e:
            logger.warning(f"Failed to parse Internshala job card: {e}")
            return None

    def _parse_salary_range(self, salary_str: str) -> tuple:
        """
        Parses Internshala salary strings into numeric bounds (min, max).
        Example: "₹ 3,00,000 - 3,50,000" -> (300000, 350000)
        """
        # Find all numbers in the string, stripping commas
        clean_str = salary_str.replace(",", "")
        numbers = re.findall(r"\d+", clean_str)
        
        if len(numbers) >= 2:
            return int(numbers[0]), int(numbers[1])
        elif len(numbers) == 1:
            return int(numbers[0]), int(numbers[0])
        return None, None

    def _parse_relative_date(self, relative_str: str) -> str:
        """
        Converts relative strings like '2 weeks ago' or 'Today' into absolute YYYY-MM-DD format.
        """
        today = datetime.now()
        relative_str = relative_str.lower().strip()
        
        if "just now" in relative_str or "today" in relative_str or "few hours" in relative_str:
            return today.strftime("%Y-%m-%d")
        if "yesterday" in relative_str or "1 day ago" in relative_str:
            return (today - timedelta(days=1)).strftime("%Y-%m-%d")
            
        # Parse "N days ago"
        match_days = re.search(r"(\d+)\s+days?\s+ago", relative_str)
        if match_days:
            days = int(match_days.group(1))
            return (today - timedelta(days=days)).strftime("%Y-%m-%d")
            
        # Parse "N weeks ago"
        match_weeks = re.search(r"(\d+)\s+weeks?\s+ago", relative_str)
        if match_weeks:
            weeks = int(match_weeks.group(1))
            return (today - timedelta(weeks=weeks)).strftime("%Y-%m-%d")
            
        # Parse "N months ago"
        match_months = re.search(r"(\d+)\s+months?\s+ago", relative_str)
        if match_months:
            months = int(match_months.group(1))
            return (today - timedelta(days=months * 30)).strftime("%Y-%m-%d")
            
        return today.strftime("%Y-%m-%d")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scraper = InternshalaScraper()
    jobs = scraper.fetch_jobs(max_pages=1)
    print(f"Scraped {len(jobs)} jobs.")
    if jobs:
        print("Sample Job:")
        import json
        # remove description for readable print
        sample = jobs[0].copy()
        sample['job_description'] = sample['job_description'][:100] + '...'
        print(json.dumps(sample, indent=2))

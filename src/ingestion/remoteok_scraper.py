import requests
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class RemoteOKScraper:
    """
    Scraper module for fetching job listings from the RemoteOK public JSON API.
    Provides structured field extraction, error handling, and schema alignment.
    """
    
    API_URL = "https://remoteok.com/api"
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "application/json"
        }

    def fetch_jobs(self) -> list:
        """
        Queries the RemoteOK JSON API and returns structured job postings.
        """
        logger.info(f"Querying RemoteOK API: {self.API_URL}")
        try:
            response = requests.get(self.API_URL, headers=self.headers, timeout=15)
            if response.status_code != 200:
                logger.error(f"RemoteOK API returned status code {response.status_code}")
                return []
            
            data = response.json()
            if not isinstance(data, list):
                logger.error("RemoteOK API response is not a list as expected.")
                return []
            
            # The first item is legal info, skip it
            jobs_raw = data[1:] if len(data) > 1 else []
            logger.info(f"Fetched {len(jobs_raw)} raw job postings from RemoteOK.")
            
            processed_jobs = []
            for job in jobs_raw:
                processed_jobs.append(self._parse_job(job))
                
            return processed_jobs
            
        except Exception as e:
            logger.error(f"Error fetching jobs from RemoteOK: {e}", exc_info=True)
            return []

    def _parse_job(self, job_dict: dict) -> dict:
        """
        Parses raw RemoteOK job dictionary into the standardized schema.
        """
        # 1. Job Title & Company
        title = job_dict.get("position", "").strip()
        company = job_dict.get("company", "").strip()
        
        # 2. Location
        location = job_dict.get("location", "").strip()
        if not location:
            location = "Remote"
            
        # 3. URL
        job_url = job_dict.get("url", "").strip()
        
        # 4. Date formatting (RemoteOK date is ISO string, e.g. '2026-06-22T02:05:03+00:00')
        raw_date = job_dict.get("date", "")
        posted_date = ""
        if raw_date:
            try:
                # Extract date component YYYY-MM-DD
                dt = datetime.fromisoformat(raw_date)
                posted_date = dt.strftime("%Y-%m-%d")
            except Exception:
                # Fallback to simple string extraction or today
                match = re.match(r"^(\d{4}-\d{2}-\d{2})", raw_date)
                if match:
                    posted_date = match.group(1)
                else:
                    posted_date = datetime.now().strftime("%Y-%m-%d")
        else:
            posted_date = datetime.now().strftime("%Y-%m-%d")

        # 5. Salary formatting and parsing
        sal_min = job_dict.get("salary_min", 0)
        sal_max = job_dict.get("salary_max", 0)
        
        # If numeric salary is provided, represent it cleanly
        salary_str = ""
        if sal_min > 0 or sal_max > 0:
            if sal_min == sal_max:
                salary_str = f"${sal_min} USD/year"
            else:
                salary_str = f"${sal_min} - ${sal_max} USD/year"
        else:
            # Check tags for salary patterns, e.g., "$100k"
            tags = job_dict.get("tags", [])
            sal_tags = [t for t in tags if "$" in t]
            if sal_tags:
                salary_str = sal_tags[0]
            else:
                salary_str = "Not Specified"

        # 6. Experience level classification
        tags = job_dict.get("tags", [])
        experience_level = self._classify_experience(title, tags, job_dict.get("description", ""))
        
        # 7. Job Description
        description = job_dict.get("description", "").strip()
        
        # Build standardized job dict
        return {
            "job_title": title,
            "company_name": company,
            "location": location,
            "experience_level": experience_level,
            "salary": salary_str,
            "job_url": job_url,
            "source_platform": "RemoteOK",
            "source_portal": "RemoteOK", # compatibility field
            "posted_date": posted_date,
            "job_description": description,
            "raw_job_description": description, # compatibility field
            # Additional keys for cleaner intake compatibility
            "salary_min": sal_min if sal_min > 0 else None,
            "salary_max": sal_max if sal_max > 0 else None,
            "salary_currency": "USD" if (sal_min > 0 or sal_max > 0) else None,
            "salary_period": "yearly" if (sal_min > 0 or sal_max > 0) else None,
            "tags": ", ".join(tags)
        }

    def _classify_experience(self, title: str, tags: list, description: str) -> str:
        """
        Classifies experience level based on title, tags, and description context.
        """
        text = (title + " " + " ".join(tags) + " " + description).lower()
        
        # Check for Fresher/Junior/Intern
        if any(term in text for term in ["intern", "internship", "fresher", "junior", "jr.", "entry level", "entry-level"]):
            return "Fresher"
        # Check for Lead/Staff/Principal
        if any(term in text for term in ["lead", "principal", "staff", "architect", "director", "manager"]):
            return "Lead"
        # Check for Senior
        if any(term in text for term in ["senior", "sr.", "sr ", "experienced"]):
            return "Senior"
            
        return "Mid-Level"

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scraper = RemoteOKScraper()
    jobs = scraper.fetch_jobs()
    print(f"Scraped {len(jobs)} jobs.")
    if jobs:
        print("Sample Job:")
        print(jobs[0])

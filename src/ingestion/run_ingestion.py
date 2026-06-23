import os
import argparse
import logging
import pandas as pd
from datetime import datetime

from src.ingestion.internshala_scraper import InternshalaScraper
from src.ingestion.remoteok_scraper import RemoteOKScraper
from src.ingestion.wellfound_scraper import WellfoundScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("ingestion_runner")

def run_ingestion(max_pages: int, output_dir: str):
    """
    Orchestrates the scraping pipeline from Internshala, RemoteOK, and Wellfound.
    Aggregates results into raw_jobs.csv, applies custom duplicate detection to
    produce cleaned_jobs.csv, and generates ingestion_report.csv.
    """
    logger.info("Initializing Enhanced Data Ingestion Module...")
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Output directory verified: {output_dir}")
    
    # 1. Fetch from RemoteOK
    logger.info("--- Starting RemoteOK Ingestion ---")
    remoteok_scraper = RemoteOKScraper()
    remoteok_jobs = remoteok_scraper.fetch_jobs()
    logger.info(f"Retrieved {len(remoteok_jobs)} jobs from RemoteOK.")
    
    # 2. Fetch from Internshala
    logger.info("--- Starting Internshala Ingestion ---")
    internshala_scraper = InternshalaScraper()
    internshala_jobs = internshala_scraper.fetch_jobs(max_pages=max_pages, rate_limit_delay=2.0)
    logger.info(f"Retrieved {len(internshala_jobs)} jobs from Internshala.")

    # 3. Fetch from Wellfound
    logger.info("--- Starting Wellfound Ingestion ---")
    wellfound_scraper = WellfoundScraper()
    wellfound_jobs = wellfound_scraper.fetch_jobs()
    logger.info(f"Retrieved {len(wellfound_jobs)} jobs from Wellfound.")

    # 4. Save Raw Jobs (before duplicate removal)
    logger.info("--- Saving Raw Dataset ---")
    all_raw_jobs = remoteok_jobs + internshala_jobs + wellfound_jobs
    raw_df = pd.DataFrame(all_raw_jobs)
    
    raw_path = os.path.join(output_dir, "raw_jobs.csv")
    raw_df.to_csv(raw_path, index=False, encoding="utf-8")
    logger.info(f"Saved all {len(all_raw_jobs)} collected jobs to {raw_path}")

    # 5. Duplicate Detection & Deduplication
    logger.info("--- Executing Custom Duplicate Detection ---")
    seen_urls = set()
    seen_combos = set()
    cleaned_jobs = []
    
    # Stats tracking per platform
    stats = {
        "RemoteOK": {"collected": len(remoteok_jobs), "duplicates": 0, "final": 0},
        "Internshala": {"collected": len(internshala_jobs), "duplicates": 0, "final": 0},
        "Wellfound": {"collected": len(wellfound_jobs), "duplicates": 0, "final": 0}
    }
    
    for job in all_raw_jobs:
        platform = job.get("source_platform", "Unknown")
        url = str(job.get("job_url", "")).strip().lower()
        title = str(job.get("job_title", "")).strip().lower()
        company = str(job.get("company_name", "")).strip().lower()
        
        # Unique identifier combination
        combo = f"{company}|{title}"
        
        is_duplicate = False
        
        # Duplicate Rule 1: job_url check
        if url and url in seen_urls:
            is_duplicate = True
            logger.debug(f"Duplicate detected via job_url: {job.get('job_url')}")
        # Duplicate Rule 2: company_name + job_title check
        elif combo in seen_combos:
            is_duplicate = True
            logger.debug(f"Duplicate detected via company+title combo: {company} | {title}")
            
        if is_duplicate:
            if platform in stats:
                stats[platform]["duplicates"] += 1
        else:
            if url:
                seen_urls.add(url)
            seen_combos.add(combo)
            cleaned_jobs.append(job)
            if platform in stats:
                stats[platform]["final"] += 1

    # Save Cleaned Jobs (after duplicate removal)
    logger.info("--- Saving Cleaned Dataset ---")
    cleaned_df = pd.DataFrame(cleaned_jobs)
    
    cleaned_path = os.path.join(output_dir, "cleaned_jobs.csv")
    cleaned_df.to_csv(cleaned_path, index=False, encoding="utf-8")
    logger.info(f"Saved {len(cleaned_jobs)} unique jobs to {cleaned_path}")

    # 6. Save Ingestion statistics Report
    logger.info("--- Generating Ingestion Statistics Report ---")
    run_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_data = []
    
    for platform, p_stats in stats.items():
        report_data.append({
            "source_platform": platform,
            "jobs_collected": p_stats["collected"],
            "duplicates_removed": p_stats["duplicates"],
            "final_unique_jobs": p_stats["final"],
            "run_date": run_date
        })
        
    # Append Total summary row
    report_data.append({
        "source_platform": "Total",
        "jobs_collected": sum(p["collected"] for p in stats.values()),
        "duplicates_removed": sum(p["duplicates"] for p in stats.values()),
        "final_unique_jobs": sum(p["final"] for p in stats.values()),
        "run_date": run_date
    })
    
    report_df = pd.DataFrame(report_data)
    report_path = os.path.join(output_dir, "ingestion_report.csv")
    report_df.to_csv(report_path, index=False, encoding="utf-8")
    
    # Log report statistics to console
    logger.info("Ingestion statistics summary:")
    logger.info(f"  * Total Collected: {sum(p['collected'] for p in stats.values())}")
    logger.info(f"  * Duplicates Removed: {sum(p['duplicates'] for p in stats.values())}")
    logger.info(f"  * Final Unique Jobs: {sum(p['final'] for p in stats.values())}")
    logger.info(f"Report written to {report_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest jobs from publicly accessible job portals with duplicate detection.")
    parser.add_argument(
        "--max-pages", 
        type=int, 
        default=10, 
        help="Maximum pages to scrape for Internshala (default: 10)"
    )
    parser.add_argument(
        "--output-dir", 
        type=str, 
        default="data/1_raw", 
        help="Directory to save raw and cleaned CSVs (default: data/1_raw)"
    )
    
    args = parser.parse_args()
    
    start_time = datetime.now()
    run_ingestion(
        max_pages=args.max_pages, 
        output_dir=args.output_dir
    )
    duration = datetime.now() - start_time
    logger.info(f"Pipeline executed in {duration.total_seconds():.2f} seconds.")

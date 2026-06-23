import os
import re
import logging
import pandas as pd
from sqlalchemy import text

from src.utils.db_connector import DBConnector
from src.pipeline.data_cleaner import DataCleaner
from src.pipeline.data_loader import DataLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("db_loader")

def parse_location_string(loc_str: str) -> tuple:
    """
    Parses a raw location string into city, state, country.
    Removes brackets/parentheses like '(Null)'.
    """
    if pd.isna(loc_str) or not isinstance(loc_str, str):
        return "Remote", "N/A", "India"
        
    parts = [p.strip() for p in loc_str.split(",")]
    if not parts or parts[0] == "":
        return "Remote", "N/A", "India"
        
    # Extract first part as city and clean it of parentheses
    city = re.sub(r"\s*\([^)]*\)", "", parts[0]).strip()
    if not city or city.lower() in ["remote", "work from home", "anywhere"]:
        return "Remote", "N/A", "India"
        
    state = "N/A"
    country = "India"
    
    if len(parts) > 1:
        state_or_country = parts[1].strip()
        # Clean state/country from parentheses too
        state_or_country = re.sub(r"\s*\([^)]*\)", "", state_or_country).strip()
        
        # Check if state_or_country is a US state abbreviation
        if len(state_or_country) == 2 and state_or_country.isupper():
            state = state_or_country
            country = "United States"
        elif state_or_country.lower() in ["us", "usa", "united states"]:
            country = "United States"
        elif state_or_country.lower() in ["uk", "united kingdom"]:
            country = "United Kingdom"
        else:
            state = state_or_country
            
    if len(parts) > 2:
        country_part = re.sub(r"\s*\([^)]*\)", "", parts[2]).strip()
        if country_part:
            country = country_part
            
    return city, state, country

def main():
    logger.info("Starting database integration process...")
    
    # 1. Initialize DB Connector and wipe/bootstrap tables
    connector = DBConnector()
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    schema_path = os.path.join(root_dir, "database", "schema_oltp.sql")
    
    logger.info("Wiping database and bootstrapping schemas...")
    if not connector.execute_raw_sql(schema_path):
        logger.error("Failed to bootstrap SQL database schema. Aborting.")
        return
        
    # 2. Read raw cleaned_jobs.csv dataset
    csv_path = os.path.join(root_dir, "data", "1_raw", "cleaned_jobs.csv")
    if not os.path.exists(csv_path):
        logger.error(f"Source file not found at: {csv_path}. Please run ingestion first.")
        return
        
    logger.info(f"Reading scraped dataset from {csv_path}...")
    raw_df = pd.read_csv(csv_path)
    logger.info(f"Loaded {len(raw_df)} postings from CSV.")
    
    # 3. Parse location column into structured location fields
    logger.info("Parsing location coordinates (city, state, country)...")
    parsed_locs = raw_df["location"].apply(lambda x: pd.Series(parse_location_string(x)))
    raw_df["city"] = parsed_locs[0]
    raw_df["state"] = parsed_locs[1]
    raw_df["country"] = parsed_locs[2]
    
    # 4. Run through DataCleaner for standardizations
    logger.info("Running DataCleaner pipeline standardizations...")
    cleaner = DataCleaner()
    cleaned_df = cleaner.clean_jobs_batch(raw_df)
    
    # 5. Load into Database using DataLoader
    logger.info("Loading cleaned records into database...")
    loader = DataLoader(connector)
    loaded_count = loader.load_cleaned_batch(cleaned_df)
    logger.info(f"Loaded {loaded_count} job postings into the database.")
    
    # 6. Retrieve statistics from database tables
    session = connector.get_session()
    try:
        companies_count = session.execute(text("SELECT COUNT(*) FROM companies")).scalar()
        locations_count = session.execute(text("SELECT COUNT(*) FROM locations")).scalar()
        jobs_count = session.execute(text("SELECT COUNT(*) FROM jobs")).scalar()
        skills_count = session.execute(text("SELECT COUNT(*) FROM skills")).scalar()
        job_skills_count = session.execute(text("SELECT COUNT(*) FROM job_skills")).scalar()
        
        print("\n==========================================")
        print("         DATABASE LOADING REPORT          ")
        print("==========================================")
        print(f"Target Database Type : {connector.db_type.upper()}")
        print(f"Companies Loaded     : {companies_count}")
        print(f"Locations Loaded     : {locations_count}")
        print(f"Jobs Loaded          : {jobs_count}")
        print(f"Skills Loaded        : {skills_count}")
        print(f"Job_Skills Loaded    : {job_skills_count}")
        print("==========================================\n")
        
    except Exception as e:
        logger.error(f"Error querying statistics: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    main()

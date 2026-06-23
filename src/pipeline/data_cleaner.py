import re
import hashlib
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class DataCleaner:
    """
    Cleans, normalizes, and transforms raw scraped or API data into clean,
    well-structured DataFrames. Demonstrates professional data engineering standards.
    """
    
    # Currency conversions (Static mapping representing exchange rates, e.g. 1 USD = 83 INR)
    USD_TO_INR = 83.0
    EUR_TO_INR = 90.0
    GBP_TO_INR = 105.0

    # Role standardizer taxonomy rules (Regex checks for standard classifications)
    ROLE_TAXONOMY = {
        "Data Analyst": r"\b(data\s+analyst|analytics\s+specialist|reporting|business\s+intelligence\s+analyst|bi\s+analyst)\b",
        "Data Engineer": r"\b(data\s+engineer|etl|big\s+data|pipeline|analytics\s+engineer|databricks|spark)\b",
        "Data Scientist": r"\b(data\s+scientist|data\s+science|predictive|quantitative\s+analyst|quant)\b",
        "ML Engineer": r"\b(machine\s+learning|ml\s+engineer|deep\s+learning|computer\s+vision|nlp|ai\s+researcher|applied\s+scientist)\b",
        "BI Engineer": r"\b(bi\s+developer|power\s+bi|tableau|business\s+intelligence\s+developer|reporting\s+engineer)\b",
        "Software Engineer": r"\b(software|developer|programmer|engineer|backend|frontend|fullstack|java|python\s+developer)\b",
    }

    # Experience level classification rules
    EXPERIENCE_TAXONOMY = {
        "Fresher": r"\b(fresher|entry|junior|jr|trainee|intern|internship|graduate|associate)\b",
        "Lead": r"\b(lead|principal|architect|director|staff|manager|vp|head)\b",
        "Senior": r"\b(senior|sr|lead|experienced|ii|iii)\b",
    }

    def clean_jobs_batch(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """
        Executes the cleaning workflow on a raw DataFrame:
        1. Drops incomplete rows
        2. Normalizes dates
        3. Cleans and standardizes salary
        4. Classifies experience level and job role
        5. Computes MD5 job hashes
        6. Removes duplicate jobs
        """
        logger.info(f"Starting cleaning workflow on {len(raw_df)} raw records.")
        df = raw_df.copy()

        # Drop rows missing crucial identifiers
        required_cols = ["job_title", "company_name", "posted_date", "source_portal"]
        for col in required_cols:
            if col not in df.columns:
                df[col] = np.nan
        df = df.dropna(subset=required_cols)

        # Initialize optional columns if missing to prevent attribute errors
        optional_cols = ["industry", "company_size_range", "salary_min", "salary_max", "salary_currency", "salary_period", "raw_job_description", "job_url"]
        for col in optional_cols:
            if col not in df.columns:
                df[col] = np.nan

        # 1. Normalize dates
        df["posted_date"] = pd.to_datetime(df["posted_date"], errors="coerce")
        df["posted_date"] = df["posted_date"].fillna(pd.Timestamp.now()).dt.date

        # 2. Clean and standardize salary columns to INR/Annual
        df = self._standardize_salaries(df)

        # 3. Classify standard role types and experience levels
        df["standardized_role"] = df["job_title"].apply(self.classify_role)
        df["experience_level"] = df.apply(lambda row: self.classify_experience(row["job_title"], row.get("experience_level", "")), axis=1)

        # 4. Normalize company size and industries
        df["industry"] = df["industry"].fillna("Unknown").str.strip().str.title()
        df["company_size_range"] = df["company_size_range"].fillna("Unknown")

        # 5. Compute Deduplication Fingerprint (MD5 Hash)
        df["job_hash"] = df.apply(self.generate_job_hash, axis=1)
        
        # Drop duplicates based on hash
        initial_count = len(df)
        df = df.drop_duplicates(subset=["job_hash"])
        logger.info(f"Cleaning complete. Deduplicated {initial_count - len(df)} duplicate job records. Remaining: {len(df)}")
        return df

    def _standardize_salaries(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates annualized, INR-standardized salary bounds.
        """
        # Ensure fields exist
        if "salary_min" not in df.columns:
            df["salary_min"] = np.nan
        if "salary_max" not in df.columns:
            df["salary_max"] = np.nan
        if "salary_currency" not in df.columns:
            df["salary_currency"] = "INR"
        if "salary_period" not in df.columns:
            df["salary_period"] = "yearly"

        # Fill currency and period defaults
        df["salary_currency"] = df["salary_currency"].fillna("INR").str.upper()
        df["salary_period"] = df["salary_period"].fillna("yearly").str.lower()

        # Handle numeric conversion
        df["salary_min"] = pd.to_numeric(df["salary_min"], errors="coerce")
        df["salary_max"] = pd.to_numeric(df["salary_max"], errors="coerce")

        # Scaling functions for each row based on currency and period
        def scale_row(row):
            min_sal = row["salary_min"]
            max_sal = row["salary_max"]
            currency = row["salary_currency"]
            period = row["salary_period"]

            if pd.isna(min_sal) and pd.isna(max_sal):
                return pd.Series([np.nan, np.nan])

            # Convert to annual based on salary frequency
            annual_multiplier = 1.0
            if period == "monthly":
                annual_multiplier = 12.0
            elif period == "hourly":
                annual_multiplier = 2000.0  # 40 hours/week * 50 weeks/year
            elif period == "daily":
                annual_multiplier = 250.0   # Standard working days

            # Currency multiplier to convert everything to INR (the base platform currency)
            currency_multiplier = 1.0
            if currency == "USD":
                currency_multiplier = self.USD_TO_INR
            elif currency in ["EUR", "EUR"]:
                currency_multiplier = self.EUR_TO_INR
            elif currency == "GBP":
                currency_multiplier = self.GBP_TO_INR

            final_min = min_sal * annual_multiplier * currency_multiplier if not pd.isna(min_sal) else np.nan
            final_max = max_sal * annual_multiplier * currency_multiplier if not pd.isna(max_sal) else np.nan

            # Data Integrity Check: If min > max, swap them
            if not pd.isna(final_min) and not pd.isna(final_max) and final_min > final_max:
                final_min, final_max = final_max, final_min

            return pd.Series([final_min, final_max])

        df[["salary_min", "salary_max"]] = df.apply(scale_row, axis=1)
        df["salary_currency"] = "INR" # Standardized output
        return df

    def classify_role(self, job_title: str) -> str:
        """
        Uses rule-based taxonomies to map raw titles into standard categorizations.
        """
        title_lower = str(job_title).lower()
        for role, pattern in self.ROLE_TAXONOMY.items():
            if re.search(pattern, title_lower):
                return role
        return "Software Engineer"  # Default fallback for overall engineering listings

    def classify_experience(self, job_title: str, current_exp: str) -> str:
        """
        Determines target career stage from title tags and current field labels.
        """
        search_str = (str(job_title) + " " + str(current_exp)).lower()
        
        # Order of checks is critical here
        if re.search(self.EXPERIENCE_TAXONOMY["Fresher"], search_str):
            return "Fresher"
        if re.search(self.EXPERIENCE_TAXONOMY["Lead"], search_str):
            return "Lead"
        if re.search(self.EXPERIENCE_TAXONOMY["Senior"], search_str):
            return "Senior"
            
        return "Mid-Level" # Default industry standard fallback

    def generate_job_hash(self, row: pd.Series) -> str:
        """
        Creates a unique MD5 hash for a job posting.
        Used as a primary key constraint to prevent duplicate database loading.
        """
        title = str(row["job_title"]).strip().lower()
        company = str(row["company_name"]).strip().lower()
        date = str(row["posted_date"])
        url = str(row.get("job_url", "")).strip().lower()
        
        raw_key = f"{title}|{company}|{date}|{url}"
        return hashlib.md5(raw_key.encode("utf-8")).hexdigest()

if __name__ == "__main__":
    # Self-test code
    cleaner = DataCleaner()
    raw_data = pd.DataFrame([
        {
            "job_title": "Python Software Engineer - Intern",
            "company_name": "TechNova Solutions",
            "posted_date": "2026-06-22",
            "source_portal": "LinkedIn",
            "salary_min": 25000,
            "salary_max": 35000,
            "salary_currency": "INR",
            "salary_period": "monthly",
            "job_url": "http://test.url/1"
        },
        {
            "job_title": "Lead Data Scientist",
            "company_name": "InnoFin Labs",
            "posted_date": "2026-06-22",
            "source_portal": "LinkedIn",
            "salary_min": 150000,
            "salary_max": 200000,
            "salary_currency": "USD",
            "salary_period": "yearly",
            "job_url": "http://test.url/2"
        }
    ])
    cleaned_df = cleaner.clean_jobs_batch(raw_data)
    print("Cleaned Data Preview:")
    print(cleaned_df[["job_title", "standardized_role", "experience_level", "salary_min", "salary_max"]])

import os
import sys
import unittest
import pandas as pd
from sqlalchemy import text

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.db_connector import DBConnector
from src.pipeline.data_cleaner import DataCleaner
from src.pipeline.data_loader import DataLoader

class TestPlacementMarketPipeline(unittest.TestCase):
    """
    Integration tests for Placement Market Intelligence pipeline.
    Validates end-to-end data flow: cleaning -> extraction -> loading -> database count checks.
    """
    @classmethod
    def setUpClass(cls):
        # Force SQLite local environment for testing
        os.environ["DB_TYPE"] = "sqlite"
        cls.connector = DBConnector()
        cls.cleaner = DataCleaner()
        cls.loader = DataLoader(cls.connector)
        
        # Load tables
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        schema_path = os.path.join(root_dir, "database", "schema_oltp.sql")
        
        # Clear database and rebuild
        success = cls.connector.execute_raw_sql(schema_path)
        assert success, "Failed to bootstrap test database schema."

    def test_pipeline_end_to_end(self):
        # 1. Prepare raw mock input batch matching scraper formats
        raw_jobs = pd.DataFrame([
            {
                "job_title": "Senior Data Scientist (NLP)",
                "company_name": "OpenAI Labs",
                "city": "Remote",
                "state": "N/A",
                "country": "Global",
                "salary_min": 180000,
                "salary_max": 240000,
                "salary_currency": "USD",
                "salary_period": "yearly",
                "source_portal": "LinkedIn",
                "raw_job_description": "We are seeking a senior scientist. Requirements: Python, Machine Learning, Deep Learning, SQL, PyTorch. Remote opportunity.",
                "posted_date": "2026-06-22",
                "job_url": "https://openai.com/jobs/nlp-scientist"
            },
            {
                "job_title": "Junior Business Intelligence Analyst",
                "company_name": "BizCorp Inc",
                "city": "Bangalore",
                "state": "Karnataka",
                "country": "India",
                "salary_min": 35000,
                "salary_max": 45000,
                "salary_currency": "INR",
                "salary_period": "monthly",
                "source_portal": "Naukri",
                "raw_job_description": "We need an associate analyst. Mandatory skills: Excel, SQL, and Power BI dashboards. Good communication skills are required.",
                "posted_date": "2026-06-21",
                "job_url": "https://bizcorp.com/jobs/bi-analyst"
            }
        ])

        # 2. Clean the batch
        cleaned_df = self.cleaner.clean_jobs_batch(raw_jobs)
        
        # Asserts on cleaned outputs
        self.assertEqual(len(cleaned_df), 2)
        self.assertEqual(cleaned_df.loc[0, "standardized_role"], "Data Scientist")
        self.assertEqual(cleaned_df.loc[0, "experience_level"], "Senior")
        self.assertEqual(cleaned_df.loc[1, "standardized_role"], "Data Analyst")
        self.assertEqual(cleaned_df.loc[1, "experience_level"], "Fresher")
        
        # Ensure salary standardizations scaled accurately
        # USD: 180k -> 180k * 83 INR = 14,940,000 INR
        self.assertAlmostEqual(cleaned_df.loc[0, "salary_min"], 180000 * 83.0)
        # INR Monthly: 35k -> 35k * 12 months = 420,000 INR
        self.assertAlmostEqual(cleaned_df.loc[1, "salary_min"], 35000 * 12.0)

        # 3. Load into Database
        loaded = self.loader.load_cleaned_batch(cleaned_df)
        self.assertEqual(loaded, 2)

        # 4. Verify Database Records
        session = self.connector.get_session()
        try:
            # Check jobs count
            jobs_count = session.execute(text("SELECT COUNT(*) FROM jobs")).scalar()
            self.assertEqual(jobs_count, 2)
            
            # Check skills extracted (Python, Machine Learning, Deep Learning, SQL, Excel, Power BI, Communication)
            skills_count = session.execute(text("SELECT COUNT(*) FROM skills")).scalar()
            self.assertTrue(skills_count > 0, "No skills were extracted into database.")
            
            # Verify junction mappings
            mapping_count = session.execute(text("SELECT COUNT(*) FROM job_skills")).scalar()
            self.assertTrue(mapping_count > 0, "No skill junction mappings created.")
            
            # Query location tiers resolved
            remote_tier = session.execute(
                text("SELECT tier FROM locations WHERE city = 'Remote'")
            ).scalar()
            self.assertEqual(remote_tier, "Tier 3")
            
            print(f"Integration verification successful! DB jobs: {jobs_count}, DB skills catalogued: {skills_count}")
        finally:
            session.close()

if __name__ == "__main__":
    unittest.main()

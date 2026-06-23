import logging
from sqlalchemy import text
from src.utils.db_connector import DBConnector
from src.pipeline.skill_extractor import SkillExtractor
import pandas as pd

logger = logging.getLogger(__name__)

class DataLoader:
    """
    Handles database inserts and upserts for standard tables.
    Maintains relational integrity by mapping parent tables before loading facts.
    """
    def __init__(self, connector: DBConnector):
        self.connector = connector
        self.extractor = SkillExtractor()

    def load_cleaned_batch(self, cleaned_df: pd.DataFrame) -> int:
        """
        Processes a cleaned DataFrame row-by-row and loads it into the database:
        1. Resolves/Creates Company
        2. Resolves/Creates Location
        3. Inserts/Upserts Job record
        4. Extracts and records job-skill mappings
        """
        logger.info(f"Initiating loader for batch of {len(cleaned_df)} jobs.")
        session = self.connector.get_session()
        loaded_count = 0

        try:
            for idx, row in cleaned_df.iterrows():
                # Extract locations (default to Country: India, State: N/A if not parsing city)
                city = row.get("city", "Remote").strip()
                state = row.get("state", "N/A").strip()
                country = row.get("country", "India").strip()
                tier = row.get("tier", "Tier 1" if city in ["Bangalore", "Mumbai", "Delhi", "Hyderabad", "Pune", "Chennai"] else "Tier 3")
                is_hub = 1 if city in ["Bangalore", "Hyderabad", "Pune", "Chennai", "Gurgaon"] else 0

                # 1. Resolve Company ID
                comp_id = self._get_or_create_company(
                    session, 
                    row["company_name"], 
                    row.get("industry", "Unknown"), 
                    row.get("company_size_range", "Unknown")
                )

                # 2. Resolve Location ID
                loc_id = self._get_or_create_location(session, city, state, country, tier, is_hub)

                # 3. Insert or Update Job Posting
                job_id = self._upsert_job(session, row, comp_id, loc_id)
                if not job_id:
                    continue  # Error occurred or job skipped

                # 4. Extract skills from description
                desc = row.get("raw_job_description", "")
                title = row["job_title"]
                skills_found = self.extractor.extract_from_text(title, desc)

                # 5. Load JobSkills mapping
                for skill_name, weight in skills_found:
                    skill_meta = self.extractor.get_skill_metadata(skill_name)
                    skill_id = self._get_or_create_skill(
                        session, 
                        skill_name, 
                        skill_meta["category"], 
                        skill_meta["difficulty"]
                    )
                    self._link_job_skill(session, job_id, skill_id, weight)

                loaded_count += 1
                
            session.commit()
            logger.info(f"Batch successfully committed. Loaded {loaded_count} job postings.")
            return loaded_count

        except Exception as e:
            session.rollback()
            logger.error(f"Error loading batch: {e}. Session rolled back.")
            raise
        finally:
            session.close()

    def _get_or_create_company(self, session, name: str, industry: str, size: str) -> int:
        """
        Finds company_id by name or creates record if missing.
        """
        # MySQL or SQLite query
        q_find = text("SELECT company_id FROM companies WHERE company_name = :name")
        res = session.execute(q_find, {"name": name}).fetchone()
        
        if res:
            return res[0]
            
        q_insert = text(
            "INSERT INTO companies (company_name, industry, company_size_range) "
            "VALUES (:name, :industry, :size)"
        )
        session.execute(q_insert, {"name": name, "industry": industry, "size": size})
        session.flush() # Populate generated IDs without full commit
        
        res = session.execute(q_find, {"name": name}).fetchone()
        return res[0]

    def _get_or_create_location(self, session, city: str, state: str, country: str, tier: str, is_hub: int) -> int:
        """
        Finds location_id or creates record if missing.
        """
        q_find = text("SELECT location_id FROM locations WHERE city = :city AND state = :state AND country = :country")
        res = session.execute(q_find, {"city": city, "state": state, "country": country}).fetchone()
        
        if res:
            return res[0]
            
        q_insert = text(
            "INSERT INTO locations (city, state, country, tier, is_tech_hub) "
            "VALUES (:city, :state, :country, :tier, :is_hub)"
        )
        session.execute(q_insert, {"city": city, "state": state, "country": country, "tier": tier, "is_hub": is_hub})
        session.flush()
        
        res = session.execute(q_find, {"city": city, "state": state, "country": country}).fetchone()
        return res[0]

    def _get_or_create_skill(self, session, skill_name: str, category: str, difficulty: str) -> int:
        """
        Finds skill_id or creates record if missing.
        """
        q_find = text("SELECT skill_id FROM skills WHERE skill_name = :name")
        res = session.execute(q_find, {"name": skill_name}).fetchone()
        
        if res:
            return res[0]
            
        q_insert = text(
            "INSERT INTO skills (skill_name, skill_category, skill_difficulty) "
            "VALUES (:name, :category, :difficulty)"
        )
        session.execute(q_insert, {"name": skill_name, "category": category, "difficulty": difficulty})
        session.flush()
        
        res = session.execute(q_find, {"name": skill_name}).fetchone()
        return res[0]

    def _upsert_job(self, session, row: pd.Series, company_id: int, location_id: int) -> int:
        """
        Inserts a job. If job_hash exists, updates the job details (upsert).
        """
        # Check if hash already exists
        q_find = text("SELECT job_id FROM jobs WHERE job_hash = :hash")
        res = session.execute(q_find, {"hash": row["job_hash"]}).fetchone()
        
        # Build parameter mapping
        params = {
            "company_id": company_id,
            "location_id": location_id,
            "job_title": row["job_title"],
            "std_role": row["standardized_role"],
            "exp_level": row["experience_level"],
            "emp_type": row.get("employment_type", "Full-Time"),
            "sal_min": row["salary_min"] if not pd.isna(row["salary_min"]) else None,
            "sal_max": row["salary_max"] if not pd.isna(row["salary_max"]) else None,
            "currency": row["salary_currency"],
            "desc": row.get("raw_job_description", ""),
            "source": row["source_portal"],
            "url": row.get("job_url", ""),
            "posted_date": row["posted_date"],
            "hash": row["job_hash"]
        }

        if res:
            # Update existing record
            job_id = res[0]
            q_update = text(
                "UPDATE jobs SET "
                "company_id = :company_id, location_id = :location_id, job_title = :job_title, "
                "standardized_role = :std_role, experience_level = :exp_level, employment_type = :emp_type, "
                "salary_min = :sal_min, salary_max = :sal_max, salary_currency = :currency, "
                "raw_job_description = :desc, source_portal = :source, job_url = :url, posted_date = :posted_date "
                "WHERE job_id = :job_id"
            )
            params["job_id"] = job_id
            session.execute(q_update, params)
            return job_id
        else:
            # Insert new record (Note: salary_avg is generated for MySQL, but we set manually in SQLite code in connector if fallback)
            # In SQLite, we handle default values. For SQLite compatibility, we calculate salary_avg here.
            # SQLite does not support generation expressions, so we compute and supply salary_avg.
            is_sqlite = (self.connector.db_type == "sqlite")
            if is_sqlite:
                avg_sal = (float(params["sal_min"] or 0) + float(params["sal_max"] or 0)) / 2
                q_insert = text(
                    "INSERT INTO jobs (company_id, location_id, job_title, standardized_role, experience_level, "
                    "employment_type, salary_min, salary_max, salary_avg, salary_currency, raw_job_description, "
                    "source_portal, job_url, posted_date, job_hash) "
                    "VALUES (:company_id, :location_id, :job_title, :std_role, :exp_level, :emp_type, "
                    ":sal_min, :sal_max, :avg_sal, :currency, :desc, :source, :url, :posted_date, :hash)"
                )
                params["avg_sal"] = avg_sal
            else:
                q_insert = text(
                    "INSERT INTO jobs (company_id, location_id, job_title, standardized_role, experience_level, "
                    "employment_type, salary_min, salary_max, salary_currency, raw_job_description, "
                    "source_portal, job_url, posted_date, job_hash) "
                    "VALUES (:company_id, :location_id, :job_title, :std_role, :exp_level, :emp_type, "
                    ":sal_min, :sal_max, :currency, :desc, :source, :url, :posted_date, :hash)"
                )
            
            session.execute(q_insert, params)
            session.flush()
            
            res_new = session.execute(q_find, {"hash": row["job_hash"]}).fetchone()
            return res_new[0]

    def _link_job_skill(self, session, job_id: int, skill_id: int, weight: float):
        """
        Creates or updates a job-skill mapping entry.
        """
        q_find = text("SELECT job_id FROM job_skills WHERE job_id = :job_id AND skill_id = :skill_id")
        res = session.execute(q_find, {"job_id": job_id, "skill_id": skill_id}).fetchone()
        
        if res:
            q_update = text(
                "UPDATE job_skills SET weight_score = :weight "
                "WHERE job_id = :job_id AND skill_id = :skill_id"
            )
            session.execute(q_update, {"job_id": job_id, "skill_id": skill_id, "weight": weight})
        else:
            q_insert = text(
                "INSERT INTO job_skills (job_id, skill_id, weight_score) "
                "VALUES (:job_id, :skill_id, :weight)"
            )
            session.execute(q_insert, {"job_id": job_id, "skill_id": skill_id, "weight": weight})

-- ============================================================================
-- SQL DDL SCHEMA - Analytical Star Schema (OLAP Views)
-- Platform: MySQL 8.0+
-- Project: Placement Market Intelligence Platform
-- ============================================================================

USE placement_intelligence_db;

-- 1. Dimension: Companies View
-- Exposes clean details of hiring companies.
CREATE OR REPLACE VIEW dim_companies_view AS
SELECT 
    company_id,
    company_name,
    industry,
    company_size_range,
    headquarters
FROM companies;

-- 2. Dimension: Locations View
-- Standardizes coordinates, region sizes, and tiers for analytics.
CREATE OR REPLACE VIEW dim_locations_view AS
SELECT 
    location_id,
    city,
    state,
    country,
    tier,
    is_tech_hub
FROM locations;

-- 3. Dimension: Skills View
-- Exposes technologies mapped to jobs.
CREATE OR REPLACE VIEW dim_skills_view AS
SELECT 
    skill_id,
    skill_name,
    skill_category,
    skill_difficulty
FROM skills;

-- 4. Dimension: Date View
-- Automatically generates calendar attributes from the unique set of job posting dates.
-- This represents an enterprise BI approach to time intelligence, bypassing complex SQL formatting.
CREATE OR REPLACE VIEW dim_date_view AS
SELECT DISTINCT
    posted_date AS date_key,
    posted_date AS date_val,
    YEAR(posted_date) AS year_val,
    QUARTER(posted_date) AS quarter_val,
    MONTH(posted_date) AS month_num,
    MONTHNAME(posted_date) AS month_name,
    WEEK(posted_date) AS week_of_year,
    DAYOFWEEK(posted_date) AS day_of_week_num,
    DAYNAME(posted_date) AS day_of_week_name,
    CASE 
        WHEN DAYOFWEEK(posted_date) IN (1, 7) THEN TRUE 
        ELSE FALSE 
    END AS is_weekend
FROM jobs;

-- 5. Fact Table: Jobs View
-- The core transactional fact containing dimensions foreign keys and measurable values.
CREATE OR REPLACE VIEW fact_jobs_view AS
SELECT 
    job_id,
    company_id,
    location_id,
    job_title,
    standardized_role,
    experience_level,
    employment_type,
    salary_min,
    salary_max,
    salary_avg,
    salary_currency,
    source_portal,
    posted_date AS date_key,
    CASE 
        WHEN experience_level IN ('Fresher', 'Internship') THEN TRUE 
        ELSE FALSE 
    END AS is_fresher_friendly,
    CASE 
        WHEN location_id IN (SELECT location_id FROM locations WHERE city = 'Remote') THEN TRUE 
        ELSE FALSE 
    END AS is_remote
FROM jobs;

-- 6. Fact Table: Job Skills (Junction Bridge)
-- Links the Fact Table (fact_jobs_view) to the Dimension Table (dim_skills_view).
CREATE OR REPLACE VIEW fact_job_skills_view AS
SELECT 
    job_id,
    skill_id,
    weight_score
FROM job_skills;

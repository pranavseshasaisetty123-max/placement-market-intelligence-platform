-- ============================================================================
-- SEED DATA SET - MySQL 8.0+
-- Project: Placement Market Intelligence Platform
-- ============================================================================

USE placement_intelligence_db;

-- Clear tables first to ensure clean execution
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE job_skills;
TRUNCATE TABLE skills;
TRUNCATE TABLE jobs;
TRUNCATE TABLE locations;
TRUNCATE TABLE companies;
SET FOREIGN_KEY_CHECKS = 1;

-- 1. Insert Companies
INSERT INTO companies (company_id, company_name, industry, company_size_range, headquarters, website_url) VALUES
(1, 'TechNova Solutions', 'IT Services', '1000-5000', 'Bangalore, IN', 'https://technova.io'),
(2, 'InnoFin Labs', 'Fintech', '100-500', 'Mumbai, IN', 'https://innofin.com'),
(3, 'Alpha Retail', 'E-commerce', '10000+', 'Seattle, US', 'https://alpharetail.com'),
(4, 'HealthQuest AI', 'Healthcare Tech', '500-1000', 'Hyderabad, IN', 'https://healthquest.org'),
(5, 'Apex Cloud Systems', 'Cloud Software', '1000-5000', 'San Francisco, US', 'https://apexcloud.com'),
(6, 'Quantum Analytics', 'Consulting', '50-200', 'Bangalore, IN', 'https://quantumanalytics.co'),
(7, 'Tata Consultancy Services', 'IT Consulting', '10000+', 'Mumbai, IN', 'https://tcs.com'),
(8, 'Infosys Technologies', 'IT Consulting', '10000+', 'Bangalore, IN', 'https://infosys.com'),
(9, 'DataVibe Consulting', 'Analytics Services', '100-500', 'Pune, IN', 'https://datavibe.com'),
(10, 'EduGlow Edtech', 'EdTech', '500-1000', 'Noida, IN', 'https://eduglow.in'),
(11, 'FinEdge Banking', 'Finance', '10000+', 'New York, US', 'https://finedge.com'),
(12, 'LogiRoute Logistics', 'Logistics', '1000-5000', 'Chennai, IN', 'https://logiroute.com'),
(13, 'BioGen Pharma', 'Pharmaceutical', '5000-10000', 'Hyderabad, IN', 'https://biogen.com'),
(14, 'CyberShield Sec', 'Cybersecurity', '100-500', 'Pune, IN', 'https://cybershield.io'),
(15, 'Target Systems', 'E-commerce', '10000+', 'Minneapolis, US', 'https://target.com');

-- 2. Insert Locations
INSERT INTO locations (location_id, city, state, country, tier, is_tech_hub) VALUES
(1, 'Bangalore', 'Karnataka', 'India', 'Tier 1', TRUE),
(2, 'Mumbai', 'Maharashtra', 'India', 'Tier 1', FALSE),
(3, 'Hyderabad', 'Telangana', 'India', 'Tier 1', TRUE),
(4, 'Pune', 'Maharashtra', 'India', 'Tier 2', TRUE),
(5, 'Chennai', 'Tamil Nadu', 'India', 'Tier 1', TRUE),
(6, 'Noida', 'Uttar Pradesh', 'India', 'Tier 2', FALSE),
(7, 'Gurgaon', 'Haryana', 'India', 'Tier 2', TRUE),
(8, 'Kolkata', 'West Bengal', 'India', 'Tier 2', FALSE),
(9, 'Remote', 'N/A', 'Global', 'N/A', FALSE),
(10, 'San Francisco', 'California', 'USA', 'Tier 1', TRUE),
(11, 'London', 'England', 'UK', 'Tier 1', FALSE);

-- 3. Insert Skills
INSERT INTO skills (skill_id, skill_name, skill_category, skill_difficulty) VALUES
(1, 'Python', 'Language', 'Intermediate'),
(2, 'SQL', 'Language', 'Intermediate'),
(3, 'Pandas', 'Library', 'Intermediate'),
(4, 'NumPy', 'Library', 'Intermediate'),
(5, 'Power BI', 'Tool', 'Intermediate'),
(6, 'Tableau', 'Tool', 'Intermediate'),
(7, 'Machine Learning', 'Domain', 'Expert'),
(8, 'Deep Learning', 'Domain', 'Expert'),
(9, 'AWS', 'Cloud', 'Intermediate'),
(10, 'Azure', 'Cloud', 'Intermediate'),
(11, 'GCP', 'Cloud', 'Intermediate'),
(12, 'Docker', 'Tool', 'Intermediate'),
(13, 'Kubernetes', 'Tool', 'Expert'),
(14, 'Git', 'Tool', 'Beginner'),
(15, 'Java', 'Language', 'Intermediate'),
(16, 'Scala', 'Language', 'Expert'),
(17, 'Apache Spark', 'Framework', 'Expert'),
(18, 'Hadoop', 'Framework', 'Expert'),
(19, 'Excel', 'Tool', 'Beginner'),
(20, 'Communication', 'Soft Skill', 'Beginner'),
(21, 'Problem Solving', 'Soft Skill', 'Intermediate'),
(22, 'C++', 'Language', 'Expert'),
(23, 'React', 'Framework', 'Intermediate'),
(24, 'TypeScript', 'Language', 'Intermediate'),
(25, 'dbt', 'Tool', 'Intermediate'),
(26, 'Airflow', 'Tool', 'Intermediate'),
(27, 'Snowflake', 'Database', 'Intermediate'),
(28, 'Data Modeling', 'Domain', 'Intermediate'),
(29, 'Data Warehousing', 'Domain', 'Expert'),
(30, 'Statistical Analysis', 'Domain', 'Intermediate');

-- 4. Insert Jobs
-- Standardized Roles: Software Engineer, Data Engineer, Data Analyst, Data Scientist, BI Engineer, ML Engineer
-- Experience Levels: Fresher, Mid-Level, Senior, Lead
INSERT INTO jobs (job_id, company_id, location_id, job_title, standardized_role, experience_level, employment_type, salary_min, salary_max, salary_currency, source_portal, job_url, posted_date, job_hash) VALUES
-- TechNova Solutions
(1, 1, 1, 'Associate Python Developer', 'Software Engineer', 'Fresher', 'Full-Time', 600000.00, 800000.00, 'INR', 'LinkedIn', 'https://linkedin.com/jobs/1', '2026-06-01', 'hash01'),
(2, 1, 1, 'Senior Data Analyst (Power BI)', 'Data Analyst', 'Senior', 'Full-Time', 1200000.00, 1600000.00, 'INR', 'Indeed', 'https://indeed.com/jobs/2', '2026-06-02', 'hash02'),
(3, 1, 9, 'Senior Data Engineer (AWS)', 'Data Engineer', 'Senior', 'Full-Time', 1800000.00, 2400000.00, 'INR', 'LinkedIn', 'https://linkedin.com/jobs/3', '2026-06-03', 'hash03'),
(4, 1, 4, 'Graduate Engineer Trainee', 'Software Engineer', 'Fresher', 'Full-Time', 450000.00, 550000.00, 'INR', 'Naukri', 'https://naukri.com/jobs/4', '2026-06-04', 'hash04'),

-- InnoFin Labs
(5, 2, 2, 'Data Analyst Intern', 'Data Analyst', 'Fresher', 'Internship', 300000.00, 420000.00, 'INR', 'Naukri', 'https://naukri.com/jobs/5', '2026-06-05', 'hash05'),
(6, 2, 2, 'Financial Quantitative Analyst', 'Data Scientist', 'Mid-Level', 'Full-Time', 1100000.00, 1500000.00, 'INR', 'Indeed', 'https://indeed.com/jobs/6', '2026-06-06', 'hash06'),
(7, 2, 9, 'Lead ML Engineer', 'ML Engineer', 'Lead', 'Full-Time', 2800000.00, 3800000.00, 'INR', 'LinkedIn', 'https://linkedin.com/jobs/7', '2026-06-07', 'hash07'),

-- Alpha Retail
(8, 3, 10, 'Data Engineer II', 'Data Engineer', 'Mid-Level', 'Full-Time', 120000.00, 150000.00, 'USD', 'LinkedIn', 'https://linkedin.com/jobs/8', '2026-06-08', 'hash08'),
(9, 3, 10, 'Applied Machine Learning Scientist', 'ML Engineer', 'Senior', 'Full-Time', 160000.00, 210000.00, 'USD', 'Indeed', 'https://indeed.com/jobs/9', '2026-06-09', 'hash09'),
(10, 3, 9, 'Senior Business Intelligence Developer', 'BI Engineer', 'Senior', 'Full-Time', 110000.00, 140000.00, 'USD', 'LinkedIn', 'https://linkedin.com/jobs/10', '2026-06-10', 'hash10'),

-- HealthQuest AI
(11, 4, 3, 'Junior Data Scientist', 'Data Scientist', 'Fresher', 'Full-Time', 700000.00, 950000.00, 'INR', 'LinkedIn', 'https://linkedin.com/jobs/11', '2026-06-11', 'hash11'),
(12, 4, 3, 'Data Analyst (Healthcare)', 'Data Analyst', 'Mid-Level', 'Full-Time', 800000.00, 1100000.00, 'INR', 'Naukri', 'https://naukri.com/jobs/12', '2026-06-12', 'hash12'),
(13, 4, 9, 'Medical Image Analyst', 'ML Engineer', 'Mid-Level', 'Full-Time', 1200000.00, 1700000.00, 'INR', 'LinkedIn', 'https://linkedin.com/jobs/13', '2026-06-13', 'hash13'),

-- Apex Cloud Systems
(14, 5, 9, 'Cloud Data Engineer', 'Data Engineer', 'Mid-Level', 'Full-Time', 1300000.00, 1800000.00, 'INR', 'Indeed', 'https://indeed.com/jobs/14', '2026-06-14', 'hash14'),
(15, 5, 10, 'Staff Software Engineer - Analytics', 'Software Engineer', 'Lead', 'Full-Time', 180000.00, 230000.00, 'USD', 'LinkedIn', 'https://linkedin.com/jobs/15', '2026-06-15', 'hash15'),

-- Quantum Analytics
(16, 6, 1, 'Data Analyst Trainee', 'Data Analyst', 'Fresher', 'Internship', 240000.00, 360000.00, 'INR', 'Naukri', 'https://naukri.com/jobs/16', '2026-06-16', 'hash16'),
(17, 6, 1, 'Analytics Consultant', 'Data Analyst', 'Mid-Level', 'Full-Time', 900000.00, 1300000.00, 'INR', 'Indeed', 'https://indeed.com/jobs/17', '2026-06-17', 'hash17'),
(18, 6, 1, 'Senior Data Specialist', 'Data Engineer', 'Senior', 'Full-Time', 1600000.00, 2200000.00, 'INR', 'LinkedIn', 'https://linkedin.com/jobs/18', '2026-06-18', 'hash18'),

-- TCS
(19, 7, 2, 'Systems Engineer - Big Data', 'Data Engineer', 'Mid-Level', 'Full-Time', 550000.00, 800000.00, 'INR', 'Naukri', 'https://naukri.com/jobs/19', '2026-06-19', 'hash19'),
(20, 7, 5, 'Assistant System Engineer (Java)', 'Software Engineer', 'Fresher', 'Full-Time', 360000.00, 450000.00, 'INR', 'Naukri', 'https://naukri.com/jobs/20', '2026-06-20', 'hash20'),
(21, 7, 8, 'Data Analyst (SQL/Excel)', 'Data Analyst', 'Fresher', 'Full-Time', 400000.00, 520000.00, 'INR', 'Naukri', 'https://naukri.com/jobs/21', '2026-06-21', 'hash21'),

-- Infosys
(22, 8, 1, 'Python Developer - Fresher', 'Software Engineer', 'Fresher', 'Full-Time', 400000.00, 500000.00, 'INR', 'LinkedIn', 'https://linkedin.com/jobs/22', '2026-06-22', 'hash22'),
(23, 8, 1, 'Technology Analyst - Power BI', 'BI Engineer', 'Mid-Level', 'Full-Time', 650000.00, 900000.00, 'INR', 'Indeed', 'https://indeed.com/jobs/23', '2026-06-22', 'hash23'),
(24, 8, 4, 'Data Scientist - Predictive Analytics', 'Data Scientist', 'Mid-Level', 'Full-Time', 950000.00, 1400000.00, 'INR', 'LinkedIn', 'https://linkedin.com/jobs/24', '2026-06-23', 'hash24'),

-- DataVibe Consulting
(25, 9, 4, 'Associate Business Analyst', 'Data Analyst', 'Fresher', 'Full-Time', 500000.00, 680000.00, 'INR', 'Naukri', 'https://naukri.com/jobs/25', '2026-06-05', 'hash25'),
(26, 9, 4, 'Senior Analytics Engineer', 'Data Engineer', 'Senior', 'Full-Time', 1400000.00, 1900000.00, 'INR', 'Indeed', 'https://indeed.com/jobs/26', '2026-06-08', 'hash26'),

-- EduGlow Edtech
(27, 10, 6, 'Curriculum Creator - Data Science', 'Data Scientist', 'Mid-Level', 'Full-Time', 600000.00, 900000.00, 'INR', 'Naukri', 'https://naukri.com/jobs/27', '2026-06-10', 'hash27'),
(28, 10, 9, 'Full Stack Web Developer', 'Software Engineer', 'Mid-Level', 'Full-Time', 800000.00, 1200000.00, 'INR', 'Indeed', 'https://indeed.com/jobs/28', '2026-06-12', 'hash28'),

-- FinEdge Banking
(29, 11, 11, 'Risk Analyst - quantitative', 'Data Scientist', 'Mid-Level', 'Full-Time', 130000.00, 175000.00, 'USD', 'LinkedIn', 'https://linkedin.com/jobs/29', '2026-06-14', 'hash29'),
(30, 11, 11, 'BI Reporting Lead', 'BI Engineer', 'Lead', 'Full-Time', 150000.00, 195000.00, 'USD', 'Indeed', 'https://indeed.com/jobs/30', '2026-06-15', 'hash30'),

-- LogiRoute Logistics
(31, 12, 5, 'Logistics Data Engineer', 'Data Engineer', 'Mid-Level', 'Full-Time', 750000.00, 1050000.00, 'INR', 'LinkedIn', 'https://linkedin.com/jobs/31', '2026-06-18', 'hash31'),
(32, 12, 5, 'Supply Chain Analyst', 'Data Analyst', 'Fresher', 'Full-Time', 480000.00, 620000.00, 'INR', 'Naukri', 'https://naukri.com/jobs/32', '2026-06-19', 'hash32'),

-- BioGen Pharma
(33, 13, 3, 'Bioinformatics Data Scientist', 'Data Scientist', 'Senior', 'Full-Time', 1600000.00, 2200000.00, 'INR', 'LinkedIn', 'https://linkedin.com/jobs/33', '2026-06-20', 'hash33'),
(34, 13, 3, 'Clinical Trial Statistician', 'Data Analyst', 'Mid-Level', 'Full-Time', 1000000.00, 1400000.00, 'INR', 'Indeed', 'https://indeed.com/jobs/34', '2026-06-21', 'hash34'),

-- CyberShield Sec
(35, 14, 4, 'Cyber Security Threat Analyst', 'Data Analyst', 'Mid-Level', 'Full-Time', 900000.00, 1250000.00, 'INR', 'Indeed', 'https://indeed.com/jobs/35', '2026-06-15', 'hash35'),
(36, 14, 4, 'Threat Intelligence ML Engineer', 'ML Engineer', 'Senior', 'Full-Time', 1700000.00, 2400000.00, 'INR', 'LinkedIn', 'https://linkedin.com/jobs/36', '2026-06-16', 'hash36'),

-- Target Systems
(37, 15, 7, 'Retail Business Analyst', 'Data Analyst', 'Fresher', 'Full-Time', 550000.00, 720000.00, 'INR', 'Naukri', 'https://naukri.com/jobs/37', '2026-06-20', 'hash37'),
(38, 15, 7, 'Principal Data Architect', 'Data Engineer', 'Lead', 'Full-Time', 2500000.00, 3600000.00, 'INR', 'LinkedIn', 'https://linkedin.com/jobs/38', '2026-06-21', 'hash38'),
(39, 15, 9, 'Senior Data Analyst (Remote)', 'Data Analyst', 'Senior', 'Full-Time', 1300000.00, 1850000.00, 'INR', 'Indeed', 'https://indeed.com/jobs/39', '2026-06-22', 'hash39'),
(40, 15, 7, 'Staff ML Scientist - Search', 'ML Engineer', 'Lead', 'Full-Time', 3000000.00, 4500000.00, 'INR', 'LinkedIn', 'https://linkedin.com/jobs/40', '2026-06-23', 'hash40');

-- 5. Insert JobSkills Junction Data
-- (job_id, skill_id, weight_score)
INSERT INTO job_skills (job_id, skill_id, weight_score) VALUES
-- Associate Python Developer (1): Python, SQL, Git, Pandas
(1, 1, 0.95),
(1, 2, 0.70),
(1, 14, 0.50),
(1, 3, 0.60),

-- Senior Data Analyst Power BI (2): SQL, Power BI, Excel, Communication, Data Modeling
(2, 2, 0.90),
(2, 5, 0.95),
(2, 19, 0.60),
(2, 20, 0.70),
(2, 28, 0.80),

-- Senior Data Engineer AWS (3): Python, SQL, AWS, Docker, dbt, Airflow, Snowflake, Data Warehousing
(3, 1, 0.80),
(3, 2, 0.85),
(3, 9, 0.95),
(3, 12, 0.70),
(3, 25, 0.80),
(3, 26, 0.85),
(3, 27, 0.90),
(3, 29, 0.90),

-- Graduate Engineer Trainee (4): Java, C++, Git, Problem Solving, Communication
(4, 15, 0.90),
(4, 22, 0.80),
(4, 14, 0.60),
(4, 21, 0.85),
(4, 20, 0.50),

-- Data Analyst Intern (5): SQL, Excel, Pandas, NumPy, Power BI
(5, 2, 0.90),
(5, 19, 0.85),
(5, 3, 0.70),
(5, 4, 0.60),
(5, 5, 0.50),

-- Financial Quantitative Analyst (6): Python, SQL, NumPy, Statistical Analysis, Problem Solving
(6, 1, 0.90),
(6, 2, 0.80),
(6, 4, 0.85),
(6, 30, 0.95),
(6, 21, 0.75),

-- Lead ML Engineer (7): Python, Machine Learning, Deep Learning, Docker, Kubernetes, GCP
(7, 1, 0.90),
(7, 7, 0.95),
(7, 8, 0.95),
(7, 12, 0.80),
(7, 13, 0.85),
(7, 11, 0.70),

-- Data Engineer II (8): Python, SQL, Apache Spark, Hadoop, AWS, Docker, Data Warehousing
(8, 1, 0.80),
(8, 2, 0.90),
(8, 17, 0.95),
(8, 18, 0.75),
(8, 9, 0.85),
(8, 12, 0.70),
(8, 29, 0.80),

-- Applied ML Scientist (9): Python, Machine Learning, Deep Learning, AWS, C++
(9, 1, 0.90),
(9, 7, 0.95),
(9, 8, 0.90),
(9, 9, 0.80),
(9, 22, 0.60),

-- Senior BI Developer (10): SQL, Power BI, Tableau, Excel, Data Warehousing, Data Modeling
(10, 2, 0.95),
(10, 5, 0.90),
(10, 6, 0.85),
(10, 19, 0.50),
(10, 29, 0.80),
(10, 28, 0.85),

-- Junior Data Scientist (11): Python, Pandas, NumPy, Machine Learning, Statistical Analysis, Communication
(11, 1, 0.95),
(11, 3, 0.85),
(11, 4, 0.80),
(11, 7, 0.85),
(11, 30, 0.75),
(11, 20, 0.60),

-- Data Analyst Healthcare (12): SQL, Excel, Tableau, Communication
(12, 2, 0.90),
(12, 19, 0.80),
(12, 6, 0.85),
(12, 20, 0.70),

-- Medical Image Analyst (13): Python, Deep Learning, Machine Learning, C++
(13, 1, 0.90),
(13, 8, 0.95),
(13, 7, 0.85),
(13, 22, 0.70),

-- Cloud Data Engineer (14): Python, SQL, AWS, Azure, dbt, Airflow
(14, 1, 0.80),
(14, 2, 0.85),
(14, 9, 0.90),
(14, 10, 0.80),
(14, 25, 0.75),
(14, 26, 0.80),

-- Staff Software Engineer - Analytics (15): Python, React, TypeScript, Java, Git, Docker
(15, 1, 0.70),
(15, 23, 0.95),
(15, 24, 0.90),
(15, 15, 0.80),
(15, 14, 0.60),
(15, 12, 0.75),

-- Data Analyst Trainee (16): SQL, Excel, Communication, Problem Solving
(16, 2, 0.85),
(16, 19, 0.90),
(16, 20, 0.80),
(16, 21, 0.70),

-- Analytics Consultant (17): SQL, Power BI, Excel, Communication, Problem Solving
(17, 2, 0.90),
(17, 5, 0.85),
(17, 19, 0.75),
(17, 20, 0.90),
(17, 21, 0.80),

-- Senior Data Specialist (18): Python, SQL, Apache Spark, Snowflake, Airflow, Data Warehousing
(18, 1, 0.85),
(18, 2, 0.90),
(18, 17, 0.95),
(18, 27, 0.85),
(18, 26, 0.80),
(18, 29, 0.90),

-- Systems Engineer - Big Data (19): Java, SQL, Hadoop, Apache Spark
(19, 15, 0.85),
(19, 2, 0.80),
(19, 18, 0.90),
(19, 17, 0.85),

-- Assistant System Engineer Java (20): Java, SQL, Git, Communication
(20, 15, 0.95),
(20, 2, 0.75),
(20, 14, 0.60),
(20, 20, 0.70),

-- Data Analyst SQL/Excel (21): SQL, Excel, Communication
(21, 2, 0.95),
(21, 19, 0.90),
(21, 20, 0.70),

-- Python Developer - Fresher (22): Python, Git, Problem Solving, Communication
(22, 1, 0.95),
(22, 14, 0.80),
(22, 21, 0.85),
(22, 20, 0.60),

-- Technology Analyst - Power BI (23): SQL, Power BI, Excel, Data Modeling
(23, 2, 0.90),
(23, 5, 0.95),
(23, 19, 0.70),
(23, 28, 0.80),

-- Data Scientist (24): Python, Pandas, Machine Learning, Statistical Analysis
(24, 1, 0.90),
(24, 3, 0.85),
(24, 7, 0.95),
(24, 30, 0.90),

-- Associate Business Analyst (25): Excel, Power BI, Communication, Problem Solving
(25, 19, 0.95),
(25, 5, 0.80),
(25, 20, 0.90),
(25, 21, 0.85),

-- Senior Analytics Engineer (26): SQL, Python, dbt, Snowflake, Airflow, Data Modeling
(26, 2, 0.90),
(26, 1, 0.80),
(26, 25, 0.95),
(26, 27, 0.90),
(26, 26, 0.85),
(26, 28, 0.90),

-- Curriculum Creator (27): Python, SQL, Machine Learning, Communication
(27, 1, 0.90),
(27, 2, 0.85),
(27, 7, 0.80),
(27, 20, 0.95),

-- Full Stack Web Developer (28): React, TypeScript, Git, Communication
(28, 23, 0.90),
(28, 24, 0.85),
(28, 14, 0.80),
(28, 20, 0.70),

-- Risk Analyst (29): Python, SQL, NumPy, Statistical Analysis
(29, 1, 0.85),
(29, 2, 0.90),
(29, 4, 0.80),
(29, 30, 0.95),

-- BI Reporting Lead (30): SQL, Power BI, Tableau, Data Modeling, Communication
(30, 2, 0.95),
(30, 5, 0.90),
(30, 6, 0.80),
(30, 28, 0.90),
(30, 20, 0.85),

-- Logistics Data Engineer (31): SQL, Python, Apache Spark, AWS, Airflow
(31, 2, 0.90),
(31, 1, 0.85),
(31, 17, 0.80),
(31, 9, 0.85),
(31, 26, 0.75),

-- Supply Chain Analyst (32): Excel, SQL, Communication, Power BI
(32, 19, 0.90),
(32, 2, 0.85),
(32, 20, 0.80),
(32, 5, 0.70),

-- Bioinformatics Data Scientist (33): Python, Pandas, Machine Learning, Statistical Analysis, Git
(33, 1, 0.95),
(33, 3, 0.90),
(33, 7, 0.90),
(33, 30, 0.95),
(33, 14, 0.70),

-- Clinical Trial Statistician (34): Python, SQL, Statistical Analysis, Communication
(34, 1, 0.85),
(34, 2, 0.80),
(34, 30, 0.95),
(34, 20, 0.80),

-- Cyber Security Threat Analyst (35): SQL, Python, Excel, Communication
(35, 2, 0.90),
(35, 1, 0.80),
(35, 19, 0.70),
(35, 20, 0.85),

-- Threat Intelligence ML Engineer (36): Python, Machine Learning, Deep Learning, Docker
(36, 1, 0.90),
(36, 7, 0.95),
(36, 8, 0.90),
(36, 12, 0.80),

-- Retail Business Analyst (37): Excel, SQL, Tableau, Communication
(37, 19, 0.90),
(37, 2, 0.85),
(37, 6, 0.80),
(37, 20, 0.90),

-- Principal Data Architect (38): SQL, Snowflake, Data Warehousing, Data Modeling, Communication
(38, 2, 0.95),
(38, 27, 0.95),
(38, 29, 0.95),
(38, 28, 0.95),
(38, 20, 0.80),

-- Senior Data Analyst (39): SQL, Python, Pandas, Power BI, Communication
(39, 2, 0.90),
(39, 1, 0.85),
(39, 3, 0.80),
(39, 5, 0.90),
(39, 20, 0.80),

-- Staff ML Scientist - Search (40): Python, Machine Learning, Deep Learning, AWS, Problem Solving
(40, 1, 0.95),
(40, 7, 0.95),
(40, 8, 0.95),
(40, 9, 0.85),
(40, 21, 0.90);

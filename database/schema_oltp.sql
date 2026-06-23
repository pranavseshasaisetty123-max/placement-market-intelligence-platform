-- ============================================================================
-- SQL DDL SCHEMA - Operational Data Store (OLTP)
-- Platform: MySQL 8.0+
-- Project: Placement Market Intelligence Platform
-- ============================================================================

-- Create and select database
CREATE DATABASE IF NOT EXISTS placement_intelligence_db;
USE placement_intelligence_db;

-- Drop tables if they exist (in reverse dependency order to avoid constraint errors)
DROP TABLE IF EXISTS job_skills;
DROP TABLE IF EXISTS skills;
DROP TABLE IF EXISTS jobs;
DROP TABLE IF EXISTS locations;
DROP TABLE IF EXISTS companies;

-- 1. Companies Table
-- Stores metadata about hiring companies.
-- Ensures uniqueness on company_name to prevent redundant insertion during scraping.
CREATE TABLE companies (
    company_id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    industry VARCHAR(100) DEFAULT 'Unknown',
    company_size_range VARCHAR(50) DEFAULT 'Unknown', -- e.g., '1-10', '11-50', '500-1000', '10000+'
    headquarters VARCHAR(150) DEFAULT 'Unknown',
    website_url VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_company_name UNIQUE (company_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Locations Table
-- Normalizes geographic locations to allow regional slicing and tier-based analysis.
-- Prevents spelling variants from causing multiple database records.
CREATE TABLE locations (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    tier VARCHAR(20) DEFAULT 'Tier 3', -- 'Tier 1', 'Tier 2', 'Tier 3', 'Remote', 'N/A'
    is_tech_hub BOOLEAN DEFAULT FALSE,
    CONSTRAINT uq_location UNIQUE (city, state, country)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Jobs Table
-- The primary transactional table storing parsed job postings.
-- Includes generated columns for avg salary and hash-based keys for deduplication.
CREATE TABLE jobs (
    job_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    location_id INT NOT NULL,
    job_title VARCHAR(255) NOT NULL,
    standardized_role VARCHAR(100) NOT NULL, -- e.g., 'Software Engineer', 'Data Analyst', 'Data Scientist'
    experience_level VARCHAR(50) NOT NULL, -- e.g., 'Fresher', 'Mid-Level', 'Senior', 'Lead'
    employment_type VARCHAR(50) DEFAULT 'Full-Time', -- e.g., 'Full-Time', 'Part-Time', 'Contract', 'Internship'
    salary_min DECIMAL(12, 2) DEFAULT NULL,
    salary_max DECIMAL(12, 2) DEFAULT NULL,
    salary_avg DECIMAL(12, 2) GENERATED ALWAYS AS ((IFNULL(salary_min, 0) + IFNULL(salary_max, 0)) / 2) STORED,
    salary_currency VARCHAR(10) DEFAULT 'INR',
    raw_job_description TEXT DEFAULT NULL,
    source_portal VARCHAR(100) NOT NULL, -- e.g., 'LinkedIn', 'Indeed', 'Naukri'
    job_url VARCHAR(512) DEFAULT NULL,
    posted_date DATE NOT NULL,
    expiry_date DATE DEFAULT NULL,
    job_hash CHAR(32) NOT NULL, -- MD5 fingerprint to prevent duplicates
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES locations(location_id) ON DELETE CASCADE,
    CONSTRAINT uq_job_hash UNIQUE (job_hash)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Indexes for performance tuning of analytical queries
CREATE INDEX idx_jobs_posted_date ON jobs(posted_date);
CREATE INDEX idx_jobs_std_role ON jobs(standardized_role);
CREATE INDEX idx_jobs_exp_level ON jobs(experience_level);
CREATE INDEX idx_jobs_company_id ON jobs(company_id);
CREATE INDEX idx_jobs_location_id ON jobs(location_id);

-- 4. Skills Table
-- A master catalog of skills across various technology sectors.
CREATE TABLE skills (
    skill_id INT AUTO_INCREMENT PRIMARY KEY,
    skill_name VARCHAR(100) NOT NULL,
    skill_category VARCHAR(50) NOT NULL, -- e.g., 'Language', 'Database', 'Cloud', 'Tool', 'Framework'
    skill_difficulty VARCHAR(20) DEFAULT 'Intermediate', -- 'Beginner', 'Intermediate', 'Expert'
    CONSTRAINT uq_skill_name UNIQUE (skill_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Index on category for rapid drill-down slicing
CREATE INDEX idx_skills_category ON skills(skill_category);

-- 5. JobSkills Junction Table
-- A high-fidelity mapping table linking jobs to skills.
-- Features a weight score indicating keyword prominence in descriptions.
CREATE TABLE job_skills (
    job_id INT NOT NULL,
    skill_id INT NOT NULL,
    weight_score DECIMAL(3, 2) DEFAULT 1.00, -- 0.00 to 1.00 importance scale
    PRIMARY KEY (job_id, skill_id),
    FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Index on skill_id for reverse search (lookup jobs containing a specific skill)
CREATE INDEX idx_job_skills_skill ON job_skills(skill_id);

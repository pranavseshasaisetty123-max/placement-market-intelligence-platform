-- ============================================================================
-- PORTFOLIO ANALYTICS QUERIES - MySQL 8.0+
-- Project: Placement Market Intelligence Platform
-- Objective: Answer core business questions for stakeholders & recruiters.
-- ============================================================================

USE placement_intelligence_db;

-- ----------------------------------------------------------------------------
-- Q1: What are the most in-demand skills?
-- Calculates the total posting count and market share percentage for each skill.
-- ----------------------------------------------------------------------------
SELECT 
    s.skill_name,
    s.skill_category,
    COUNT(js.job_id) AS job_postings_count,
    ROUND((COUNT(js.job_id) * 100.0) / (SELECT COUNT(*) FROM jobs), 2) AS market_demand_share_pct
FROM skills s
LEFT JOIN job_skills js ON s.skill_id = js.skill_id
GROUP BY s.skill_id, s.skill_name, s.skill_category
ORDER BY job_postings_count DESC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- Q2: Which companies hire the most candidates?
-- Identifies top hiring corporations based on posted job volume.
-- ----------------------------------------------------------------------------
SELECT 
    c.company_name,
    c.industry,
    COUNT(j.job_id) AS total_job_postings,
    ROUND(AVG(j.salary_avg), 0) AS average_offered_salary_inr
FROM companies c
JOIN jobs j ON c.company_id = j.company_id
GROUP BY c.company_id, c.company_name, c.industry
ORDER BY total_job_postings DESC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- Q3: Which locations have the highest number of opportunities?
-- Groups openings by city, state, and tier to identify geographical tech hubs.
-- ----------------------------------------------------------------------------
SELECT 
    l.city,
    l.state,
    l.tier,
    l.is_tech_hub,
    COUNT(j.job_id) AS openings_count,
    ROUND((COUNT(j.job_id) * 100.0) / (SELECT COUNT(*) FROM jobs), 2) AS regional_share_pct
FROM locations l
JOIN jobs j ON l.location_id = j.location_id
GROUP BY l.location_id, l.city, l.state, l.tier, l.is_tech_hub
ORDER BY openings_count DESC;

-- ----------------------------------------------------------------------------
-- Q4: What skills are associated with higher salaries?
-- Lists skills ordered by the average salary of jobs mentioning them.
-- Shows ONLY skills with a minimum of 2 job postings to avoid single-posting outliers.
-- ----------------------------------------------------------------------------
SELECT 
    s.skill_name,
    s.skill_category,
    COUNT(js.job_id) AS sample_postings_count,
    ROUND(AVG(j.salary_avg), 0) AS avg_annual_salary_inr,
    ROUND(AVG(j.salary_avg) - (SELECT AVG(salary_avg) FROM jobs), 0) AS salary_variance_vs_global_avg
FROM skills s
JOIN job_skills js ON s.skill_id = js.skill_id
JOIN jobs j ON js.job_id = j.job_id
GROUP BY s.skill_id, s.skill_name, s.skill_category
HAVING sample_postings_count >= 2
ORDER BY avg_annual_salary_inr DESC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- Q5: Which skills frequently appear together in job postings?
-- Calculates co-occurrence combinations. Self-joins job_skills on job_id.
-- ----------------------------------------------------------------------------
SELECT 
    s1.skill_name AS skill_a,
    s2.skill_name AS skill_b,
    COUNT(*) AS co_occurrence_count,
    ROUND((COUNT(*) * 100.0) / (SELECT COUNT(*) FROM jobs), 2) AS co_occurrence_market_share_pct
FROM job_skills js1
JOIN job_skills js2 ON js1.job_id = js2.job_id AND js1.skill_id < js2.skill_id
JOIN skills s1 ON js1.skill_id = s1.skill_id
JOIN skills s2 ON js2.skill_id = s2.skill_id
GROUP BY s1.skill_name, s2.skill_name
ORDER BY co_occurrence_count DESC
LIMIT 15;

-- ----------------------------------------------------------------------------
-- Q6: What are the fastest-growing skills and roles?
-- Tracks hiring momentum by comparing weekly posting velocities.
-- ----------------------------------------------------------------------------
SELECT 
    standardized_role,
    COUNT(CASE WHEN posted_date >= '2026-06-15' THEN 1 END) AS current_week_volume,
    COUNT(CASE WHEN posted_date < '2026-06-15' AND posted_date >= '2026-06-01' THEN 1 END) AS prior_weeks_volume,
    -- Simple momentum ratio
    ROUND(
        (COUNT(CASE WHEN posted_date >= '2026-06-15' THEN 1 END) * 100.0) / 
        NULLIF(COUNT(CASE WHEN posted_date < '2026-06-15' AND posted_date >= '2026-06-01' THEN 1 END), 0), 
        2
    ) AS weekly_velocity_ratio
FROM jobs
GROUP BY standardized_role
ORDER BY weekly_velocity_ratio DESC;

-- ----------------------------------------------------------------------------
-- Q7: Which roles are most common for freshers?
-- Identifies entry-level targets using the Fresher Accessibility Ratio (FAR).
-- ----------------------------------------------------------------------------
SELECT 
    standardized_role,
    COUNT(CASE WHEN experience_level IN ('Fresher', 'Internship') THEN 1 END) AS fresher_openings,
    COUNT(*) AS total_openings,
    ROUND(
        (COUNT(CASE WHEN experience_level IN ('Fresher', 'Internship') THEN 1 END) * 100.0) / COUNT(*), 
        2
    ) AS fresher_accessibility_ratio_pct
FROM jobs
GROUP BY standardized_role
ORDER BY fresher_accessibility_ratio_pct DESC, total_openings DESC;

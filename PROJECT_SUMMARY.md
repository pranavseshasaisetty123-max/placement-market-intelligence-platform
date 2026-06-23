# Project Summary: Placement Market Intelligence Platform

A high-level overview of the platform designed for recruiters and hiring managers.

---

## 1. Problem Statement
Job seekers and college placement offices operate with significant information asymmetry. Standard job portals contain unstructured descriptions, list salaries across inconsistent frequencies and currencies, and are cluttered with duplicate listings. Consequently, candidates lack data-driven clarity on true **skill demand share**, **salary premiums**, and **geographical hiring tiers**.

## 2. The Solution
The **Placement Market Intelligence Platform** is an end-to-end data engineering and analytics dashboard. It automates the collection of raw job listings from public portals, executes ETL transformations to standardize salaries into annualized INR, cleans duplicate postings, and extracts key technical skills. The structured data is stored in a relational database and visualized on an interactive dashboard to identify high-volume hiring hubs and salary-driving technologies.

## 3. Core System Architecture
The platform is designed around a multi-stage data architecture:
1.  **Ingestion (Bronze)**: Custom Python scrapers query RemoteOK's JSON API and scrape Internshala's HTML page (using BeautifulSoup). It features safe-failing error handlers that skip blocked connections (Wellfound 403 blocks) and log the event.
2.  **ETL & Transformation (Silver)**: A Pandas transformation pipeline filters duplicates by URL and company-title combinations. It standardizes relative post dates to absolute formats, parses multi-currency salaries into unified Annualized INR, maps career stages, and calculates an MD5 fingerprint hash to enforce relational integrity.
3.  **Analytics Storage (Gold)**: A relational database loader maps listings into an **OLAP Star Schema** with indexes on keys frequently used in filters.
4.  **Presentation UI**: A dark-themed Streamlit web application that fetches data from the database cache and displays geographic hubs, skill co-occurrence heatmaps, and salary premiums.

## 4. Integrated Dataset Metrics
The platform operates on a real-time dataset loaded into the production SQLite core:
*   **Job Postings**: 491
*   **Active Hiring Companies**: 361
*   **Distinct Geographic Locations**: 158
*   **Catalogued Skills**: 27
*   **Job-Skill Junction Mappings**: 364

## 5. Key Performance Indicators (KPIs)
*   **Average Annual Salary**: ₹784,620.64
*   **Fresher Accessibility Ratio (FAR)**: 24.64% *(percentage of total postings accessible to freshers and interns)*

## 6. Strategic Business Value
*   **Friction Reduction**: Consolidates postings from diverse portals, reducing job search overhead.
*   **Skill Optimization**: Identifies which technology pairings (e.g. Python & SQL) command the highest salary premiums, helping candidates optimize learning paths.
*   **Geographic Slicing**: Identifies tier-based hiring hubs, showing where specific roles are concentrated.

## 7. Technologies & Skills Demonstrated
*   **Programming**: Python (Requests, BeautifulSoup, NumPy).
*   **Data Wrangling**: Pandas (Batch cleaning, Lambda scaling, Grouping).
*   **Database Design**: SQLite/MySQL, Star Schema, Surrogate/Composite Keys, Unique Constraints, Database Indexes.
*   **Orchestration & UI**: Streamlit caching (`@st.cache_data`), Plotly Express charts.
*   **Systems Resiliency**: Rate limiting, fail-safe HTTP error handling (403 bypass).

## 8. Why This Project Is Resume-Worthy
This is not a mock project built on clean CSVs; it is a **production-ready pipeline** dealing with messy, real-world data. It showcases the ability to handle scraping rate limits, parse irregular HTML, structure normalized relational databases, execute complex SQL analytical joins, and expose insights in a premium, high-fidelity user interface.

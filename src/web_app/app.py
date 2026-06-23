import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

# Add root folder to python path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.utils.db_connector import DBConnector

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Placement Market Intelligence Platform",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for Premium Aesthetics
st.markdown("""
    <style>
        .main {
            background-color: #0f1115;
            color: #e2e8f0;
        }
        .stMetric {
            background-color: #1a1e26;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #2e3748;
        }
        .css-1kyx601-stVerticalBlock {
            gap: 1.5rem;
        }
        h1, h2, h3 {
            font-family: 'Inter', sans-serif;
            color: #ffffff;
            font-weight: 700;
        }
        .subheader-text {
            color: #a0aec0;
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #1a1e26;
            border-radius: 4px 4px 0px 0px;
            padding: 10px 20px;
            color: #a0aec0;
            border: 1px solid #2e3748;
        }
        .stTabs [aria-selected="true"] {
            background-color: #4f46e5 !important;
            color: white !important;
            border-color: #4f46e5 !important;
        }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Database Bootstrap and Session Setup
# -----------------------------------------------------------------------------
@st.cache_resource
def get_db_connection():
    connector = DBConnector()
    # Check if tables exist. If not, bootstrap the SQLite/MySQL database
    session = connector.get_session()
    try:
        # Check if jobs table exists
        session.execute(text("SELECT 1 FROM jobs LIMIT 1"))
    except Exception:
        st.info("Database is uninitialized. Bootstrapping schemas and inserting seed data...")
        # Get path of DDL scripts
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        schema_path = os.path.join(root_dir, "database", "schema_oltp.sql")
        seed_path = os.path.join(root_dir, "database", "seed_data.sql")
        
        # Run bootstrapping
        connector.execute_raw_sql(schema_path)
        connector.execute_raw_sql(seed_path)
        st.success("Database successfully initialized with seed datasets!")
    finally:
        session.close()
    return connector

# Import SQL text utility dynamically
from sqlalchemy import text

connector = get_db_connection()
engine = connector.engine

# -----------------------------------------------------------------------------
# Data Ingestion for Dashboard (using Views/Tables)
# -----------------------------------------------------------------------------
@st.cache_data(ttl=600)
def load_dashboard_data():
    # Load primary datasets
    query_jobs = """
        SELECT 
            j.job_id,
            j.job_title,
            j.standardized_role,
            j.experience_level,
            j.employment_type,
            j.salary_min,
            j.salary_max,
            j.salary_avg,
            j.posted_date,
            c.company_name,
            c.industry,
            c.company_size_range,
            l.city,
            l.state,
            l.country,
            l.tier,
            l.is_tech_hub
        FROM jobs j
        JOIN companies c ON j.company_id = c.company_id
        JOIN locations l ON j.location_id = l.location_id
    """
    
    query_skills = """
        SELECT 
            js.job_id,
            s.skill_name,
            s.skill_category,
            s.skill_difficulty,
            js.weight_score
        FROM job_skills js
        JOIN skills s ON js.skill_id = s.skill_id
    """
    
    df_jobs = pd.read_sql(query_jobs, engine)
    df_skills = pd.read_sql(query_skills, engine)
    
    # Cast datatypes
    df_jobs["posted_date"] = pd.to_datetime(df_jobs["posted_date"])
    
    return df_jobs, df_skills

# Fetch original datasets
df_jobs_raw, df_skills_raw = load_dashboard_data()

# -----------------------------------------------------------------------------
# Sidebar Filtering Layout
# -----------------------------------------------------------------------------
st.sidebar.image("https://img.icons8.com/isometric/100/database.png", width=70)
st.sidebar.title("Filters")
st.sidebar.markdown("Sift through data analytics subsets:")

# Filter values
roles_list = sorted(df_jobs_raw["standardized_role"].unique())
cities_list = sorted(df_jobs_raw["city"].unique())
exp_list = sorted(df_jobs_raw["experience_level"].unique())

selected_roles = st.sidebar.multiselect("Standardized Role", roles_list, default=roles_list)
selected_cities = st.sidebar.multiselect("Job Location", cities_list, default=cities_list)
selected_exp = st.sidebar.multiselect("Experience Level", exp_list, default=exp_list)

# Apply filters
df_jobs = df_jobs_raw[
    (df_jobs_raw["standardized_role"].isin(selected_roles)) &
    (df_jobs_raw["city"].isin(selected_cities)) &
    (df_jobs_raw["experience_level"].isin(selected_exp))
]

# Filter skill mappings accordingly
df_skills = df_skills_raw[df_skills_raw["job_id"].isin(df_jobs["job_id"])]

# -----------------------------------------------------------------------------
# Header Layout
# -----------------------------------------------------------------------------
st.title("💼 Placement Market Intelligence Platform")
st.markdown("<div class='subheader-text'>Real-time hiring data & skill demand analytics dashboard for freshers and career guidance.</div>", unsafe_allow_html=True)

if df_jobs.empty:
    st.warning("No records matched the selected filter criteria. Resetting display...")
    st.stop()

# -----------------------------------------------------------------------------
# Key Metric Cards (Row 1)
# -----------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Job Postings", value=f"{len(df_jobs)}")
with col2:
    avg_salary_inr = df_jobs["salary_avg"].mean()
    st.metric(label="Average Annual Salary", value=f"₹{avg_salary_inr:,.0f}" if not pd.isna(avg_salary_inr) else "N/A")
with col3:
    companies_count = df_jobs["company_name"].nunique()
    st.metric(label="Active Hiring Companies", value=f"{companies_count}")
with col4:
    fresher_jobs = df_jobs[df_jobs["experience_level"].isin(["Fresher", "Internship"])]
    far_metric = (len(fresher_jobs) / len(df_jobs)) * 100 if len(df_jobs) > 0 else 0
    st.metric(label="Fresher Accessibility Ratio (FAR)", value=f"{far_metric:.1f}%")

st.write("---")

# -----------------------------------------------------------------------------
# Tabs Layout
# -----------------------------------------------------------------------------
tab_market, tab_skills, tab_bundles, tab_search = st.tabs([
    "📈 Market & Geographies", 
    "🎯 Skill Demand & Salary Premiums", 
    "🔗 Skill Bundling (Co-occurrence)", 
    "🔍 Job Search & Trends"
])

# =============================================================================
# Tab 1: Market & Geography
# =============================================================================
with tab_market:
    st.subheader("Market Scope & Location Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Chart: Job volume by location
        df_loc = df_jobs.groupby("city").size().reset_index(name="job_count").sort_values("job_count", ascending=True)
        fig_loc = px.bar(
            df_loc, 
            y="city", 
            x="job_count", 
            orientation="h",
            title="Job Postings by Geographic Hubs",
            labels={"job_count": "Number of Postings", "city": "City"},
            color="job_count",
            color_continuous_scale="Purples"
        )
        fig_loc.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig_loc, use_container_width=True)
        
    with col2:
        # Chart: Company market share
        df_comp = df_jobs.groupby("company_name").size().reset_index(name="job_count").sort_values("job_count", ascending=False).head(10)
        fig_comp = px.bar(
            df_comp, 
            x="company_name", 
            y="job_count",
            title="Top Hiring Companies (Volume)",
            labels={"job_count": "Number of Postings", "company_name": "Company"},
            color="job_count",
            color_continuous_scale="Blues"
        )
        fig_comp.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig_comp, use_container_width=True)

    col3, col4 = st.columns([1, 1])
    
    with col3:
        # Industry shares
        df_ind = df_jobs.groupby("industry").size().reset_index(name="count")
        fig_ind = px.pie(
            df_ind, 
            names="industry", 
            values="count",
            title="Job Openings Distribution by Industry",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_ind.update_layout(template="plotly_dark", height=380)
        st.plotly_chart(fig_ind, use_container_width=True)

    with col4:
        # Tier wise opportunities
        df_tier = df_jobs.groupby("tier").size().reset_index(name="count")
        fig_tier = px.pie(
            df_tier,
            names="tier",
            values="count",
            title="Hiring Activity across Tier Hubs vs Remote",
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_tier.update_layout(template="plotly_dark", height=380)
        st.plotly_chart(fig_tier, use_container_width=True)

# =============================================================================
# Tab 2: Skill Demand & Salary Premiums
# =============================================================================
with tab_skills:
    st.subheader("Skill Requirements & Salary Optimization Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 15 in-demand skills
        df_skill_count = df_skills.groupby("skill_name").size().reset_index(name="frequency").sort_values("frequency", ascending=False).head(15)
        df_skill_count["demand_share_pct"] = (df_skill_count["frequency"] / len(df_jobs)) * 100
        
        fig_skills = px.bar(
            df_skill_count, 
            x="demand_share_pct", 
            y="skill_name", 
            orientation="h",
            title="Top 15 Most Demanded Skills (% of Job Listings)",
            labels={"demand_share_pct": "% of Job Listings", "skill_name": "Skill"},
            color="demand_share_pct",
            color_continuous_scale="Viridis"
        )
        fig_skills.update_layout(template="plotly_dark", yaxis={'categoryorder':'total ascending'}, height=400)
        st.plotly_chart(fig_skills, use_container_width=True)

    with col2:
        # Fresher friendly roles
        df_fresher_roles = df_jobs[df_jobs["experience_level"].isin(["Fresher", "Internship"])]
        df_fresher_roles = df_fresher_roles.groupby("standardized_role").size().reset_index(name="fresher_postings")
        df_total_roles = df_jobs.groupby("standardized_role").size().reset_index(name="total_postings")
        
        df_far = pd.merge(df_fresher_roles, df_total_roles, on="standardized_role")
        df_far["fresher_accessibility_pct"] = (df_far["fresher_postings"] / df_far["total_postings"]) * 100
        df_far = df_far.sort_values("fresher_accessibility_pct", ascending=False)
        
        fig_far = px.bar(
            df_far,
            x="standardized_role",
            y="fresher_accessibility_pct",
            title="Fresher Accessibility Ratio (FAR %) by Standard Role",
            labels={"fresher_accessibility_pct": "FAR %", "standardized_role": "Standardized Role"},
            color="fresher_accessibility_pct",
            color_continuous_scale="Tealgrn"
        )
        fig_far.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig_far, use_container_width=True)

    st.subheader("High-Pay Skills Analysis (Salary Premium Index)")
    st.markdown("We assess skills that correlate with higher compensation inside the same filtered set of jobs:")
    
    # Calculate Average Salary for jobs requiring each skill
    skill_salary_data = []
    for skill in df_skills["skill_name"].unique():
        job_ids_with_skill = df_skills[df_skills["skill_name"] == skill]["job_id"]
        avg_sal = df_jobs[df_jobs["job_id"].isin(job_ids_with_skill)]["salary_avg"].mean()
        job_count = len(job_ids_with_skill)
        
        if not pd.isna(avg_sal) and job_count >= 2: # Keep skills with enough samples
            skill_salary_data.append({
                "Skill": skill,
                "Avg Annual Salary": avg_sal,
                "Sample Postings": job_count,
                "Category": df_skills_raw[df_skills_raw["skill_name"] == skill]["skill_category"].iloc[0]
            })
            
    df_skill_sal = pd.DataFrame(skill_salary_data).sort_values("Avg Annual Salary", ascending=False)
    
    if not df_skill_sal.empty:
        fig_scat = px.scatter(
            df_skill_sal,
            x="Sample Postings",
            y="Avg Annual Salary",
            size="Sample Postings",
            color="Category",
            hover_name="Skill",
            title="Salary Premium Scatter Plot (Salary vs Skill Frequencies)",
            size_max=35,
            color_discrete_sequence=px.colors.qualitative.Dark24
        )
        fig_scat.add_hline(y=avg_salary_inr, line_dash="dash", line_color="orange", annotation_text="Global Avg Salary")
        fig_scat.update_layout(template="plotly_dark", height=450)
        st.plotly_chart(fig_scat, use_container_width=True)
    else:
        st.info("Insufficient salary data to compute premium ratios.")

# =============================================================================
# Tab 3: Skill Bundling (Co-occurrence)
# =============================================================================
with tab_bundles:
    st.subheader("Skill Co-occurrence Network & Heatmap Analysis")
    st.markdown("Identifies technology pairings that frequently appear together in the job market, helping seekers choose optimal course paths:")

    # Prepare Co-occurrence Matrix
    # We join df_skills with itself on job_id to get all skill pairs inside the same job posting
    df_pairs = pd.merge(df_skills, df_skills, on="job_id", suffixes=('_a', '_b'))
    
    # Filter out self-pairs (e.g. Python matched with Python)
    df_pairs = df_pairs[df_pairs["skill_name_a"] != df_pairs["skill_name_b"]]
    
    # Group by pairs
    cooc_matrix = df_pairs.groupby(["skill_name_a", "skill_name_b"]).size().reset_index(name="count")
    
    # Take top 12 skills for cleaner heatmap matrix representation
    top_skills_list = df_skills.groupby("skill_name").size().sort_values(ascending=False).head(12).index.tolist()
    
    if len(top_skills_list) > 1:
        # Create a pivoted DataFrame grid
        grid_df = pd.DataFrame(0, index=top_skills_list, columns=top_skills_list)
        
        for idx, row in cooc_matrix.iterrows():
            sa, sb = row["skill_name_a"], row["skill_name_b"]
            if sa in top_skills_list and sb in top_skills_list:
                grid_df.loc[sa, sb] = row["count"]
                
        # Plot Heatmap
        fig_heat = go.Figure(data=go.Heatmap(
            z=grid_df.values,
            x=grid_df.columns,
            y=grid_df.index,
            colorscale='Hot',
            hoverongaps = False
        ))
        fig_heat.update_layout(
            title="Top 12 Skill Co-occurrence Heatmap (Joint Job Counts)",
            template="plotly_dark",
            height=500
        )
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.info("Not enough co-occurring skill pairs to build a correlation heatmap.")

# =============================================================================
# Tab 4: Growth Trends & Job Search
# =============================================================================
with tab_search:
    st.subheader("Hiring Volume Velocity & Momentum")
    
    # Hiring momentum over time
    df_time = df_jobs.groupby(df_jobs["posted_date"].dt.to_period("W")).size().reset_index(name="count")
    df_time["posted_date"] = df_time["posted_date"].dt.to_timestamp()
    
    fig_time = px.line(
        df_time,
        x="posted_date",
        y="count",
        title="Weekly Hiring Postings Volume (Velocity Trend)",
        labels={"count": "New Postings", "posted_date": "Week Commencing"},
        markers=True,
        line_shape="spline"
    )
    fig_time.update_traces(line_color="#4f46e5", line_width=3)
    fig_time.update_layout(template="plotly_dark", height=350)
    st.plotly_chart(fig_time, use_container_width=True)
    
    st.write("---")
    st.subheader("Job Search Directory")
    st.markdown("Scan individual job postings that matched your filters:")
    
    # Display table of raw matched positions
    search_cols = ["company_name", "job_title", "standardized_role", "experience_level", "city", "salary_min", "salary_max", "posted_date"]
    df_search_grid = df_jobs[search_cols].copy()
    
    # Format dates and salaries nicely for presentation grid
    df_search_grid["posted_date"] = df_search_grid["posted_date"].dt.strftime("%Y-%m-%d")
    df_search_grid["salary_min"] = df_search_grid["salary_min"].map(lambda x: f"₹{x:,.0f}" if not pd.isna(x) else "N/A")
    df_search_grid["salary_max"] = df_search_grid["salary_max"].map(lambda x: f"₹{x:,.0f}" if not pd.isna(x) else "N/A")
    
    df_search_grid.columns = [
        "Company", "Job Title", "Standard Role", "Experience Level", "City", "Min Salary", "Max Salary", "Posted Date"
    ]
    
    st.dataframe(df_search_grid, use_container_width=True, hide_index=True)

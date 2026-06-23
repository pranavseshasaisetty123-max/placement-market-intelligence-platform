import re
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class SkillExtractor:
    """
    NLP and pattern-matching system that scans job titles and descriptions to extract
    standardized skills. Prevents false positive matches (e.g., separating 'Go' from 'Google').
    """
    def __init__(self):
        # Catalog of skills with category, difficulty, and boundary regexes.
        # This catalog matches the database seed skills.
        self.skills_catalog = {
            "Python": {"category": "Language", "difficulty": "Intermediate", "regex": r"\bpython\b"},
            "SQL": {"category": "Language", "difficulty": "Intermediate", "regex": r"\bsql\b|\bpostgresql\b|\bmysql\b|\bsqlite\b"},
            "Pandas": {"category": "Library", "difficulty": "Intermediate", "regex": r"\bpandas\b"},
            "NumPy": {"category": "Library", "difficulty": "Intermediate", "regex": r"\bnumpy\b"},
            "Power BI": {"category": "Tool", "difficulty": "Intermediate", "regex": r"\bpower\s*bi\b|\bpbi\b"},
            "Tableau": {"category": "Tool", "difficulty": "Intermediate", "regex": r"\btableau\b"},
            "Machine Learning": {"category": "Domain", "difficulty": "Expert", "regex": r"\bmachine\s+learning\b|\bml\b"},
            "Deep Learning": {"category": "Domain", "difficulty": "Expert", "regex": r"\bdeep\s+learning\b|\bdl\b|\bneural\s+networks\b"},
            "AWS": {"category": "Cloud", "difficulty": "Intermediate", "regex": r"\baws\b|\bamazon\s+web\s+services\b"},
            "Azure": {"category": "Cloud", "difficulty": "Intermediate", "regex": r"\bazure\b|\bmicrosoft\s+azure\b"},
            "GCP": {"category": "Cloud", "difficulty": "Intermediate", "regex": r"\bgcp\b|\bgoogle\s+cloud\b"},
            "Docker": {"category": "Tool", "difficulty": "Intermediate", "regex": r"\bdocker\b"},
            "Kubernetes": {"category": "Tool", "difficulty": "Expert", "regex": r"\bkubernetes\b|\bk8s\b"},
            "Git": {"category": "Tool", "difficulty": "Beginner", "regex": r"\bgit\b|\bgithub\b|\bgitlab\b"},
            "Java": {"category": "Language", "difficulty": "Intermediate", "regex": r"\bjava\b(?!script)"}, # Exclude javascript
            "Scala": {"category": "Language", "difficulty": "Expert", "regex": r"\bscala\b"},
            "Apache Spark": {"category": "Framework", "difficulty": "Expert", "regex": r"\bspark\b|\bapache\s+spark\b|\bpyspark\b"},
            "Hadoop": {"category": "Framework", "difficulty": "Expert", "regex": r"\bhadoop\b|\bmapreduce\b"},
            "Excel": {"category": "Tool", "difficulty": "Beginner", "regex": r"\bexcel\b|\bspreadsheets\b"},
            "Communication": {"category": "Soft Skill", "difficulty": "Beginner", "regex": r"\bcommunication\b|\binterpersonal\b|\bpresentation\b"},
            "Problem Solving": {"category": "Soft Skill", "difficulty": "Intermediate", "regex": r"\bproblem\s+solving\b|\banalytical\s+skills\b|\btroubleshooting\b"},
            "C++": {"category": "Language", "difficulty": "Expert", "regex": r"\bc\+\+\b|\bcpp\b"},
            "React": {"category": "Framework", "difficulty": "Intermediate", "regex": r"\breact\b|\breactjs\b"},
            "TypeScript": {"category": "Language", "difficulty": "Intermediate", "regex": r"\btypescript\b|\bts\b"},
            "dbt": {"category": "Tool", "difficulty": "Intermediate", "regex": r"\bdbt\b|\bdata\s+build\s+tool\b"},
            "Airflow": {"category": "Tool", "difficulty": "Intermediate", "regex": r"\bairflow\b|\bapache\s+airflow\b"},
            "Snowflake": {"category": "Database", "difficulty": "Intermediate", "regex": r"\bsnowflake\b"},
            "Data Modeling": {"category": "Domain", "difficulty": "Intermediate", "regex": r"\bdata\s+modeling\b|\bdimensional\s+modeling\b|\berd\b"},
            "Data Warehousing": {"category": "Domain", "difficulty": "Expert", "regex": r"\bdata\s+warehousing\b|\bdwh\b|\bdata\s+warehouse\b"},
            "Statistical Analysis": {"category": "Domain", "difficulty": "Intermediate", "regex": r"\bstatistical\b|\bstatistics\b|\bhypothesis\s+testing\b"},
        }
        
        # Compile expressions for high performance
        self.compiled_rules = {
            skill: re.compile(meta["regex"], re.IGNORECASE) 
            for skill, meta in self.skills_catalog.items()
        }

    def extract_from_text(self, title: str, description: str) -> List[Tuple[str, float]]:
        """
        Scans both the job title and job description to extract matched skills and assign weights.
        Returns a list of tuples: [(skill_name, weight_score)]
        
        Weight Rules:
        - Mention in Title: 1.00 weight (highest priority).
        - Mention in Description: Base 0.70 weight + 0.15 bonus if mentioned multiple times.
        """
        matched_skills = []
        text_desc = str(description).lower()
        text_title = str(title).lower()
        
        for skill_name, pattern in self.compiled_rules.items():
            in_title = bool(pattern.search(text_title))
            in_desc = len(pattern.findall(text_desc)) # Returns frequency count
            
            if in_title or in_desc > 0:
                # Calculate importance weight
                if in_title:
                    weight = 1.00
                else:
                    # Multi-mention bonus up to 0.90 max
                    weight = min(0.70 + (in_desc * 0.05), 0.90)
                
                matched_skills.append((skill_name, weight))
                
        return matched_skills

    def get_skill_metadata(self, skill_name: str) -> Dict[str, str]:
        """
        Returns classification info (category, difficulty) for a skill.
        """
        return self.skills_catalog.get(skill_name, {
            "category": "Unknown",
            "difficulty": "Intermediate"
        })

if __name__ == "__main__":
    extractor = SkillExtractor()
    sample_title = "Junior Python & Power BI Developer"
    sample_desc = "We need a python engineer with experience in SQL databases. They will build dashboards with Power BI. Power BI experience is essential. Communication skills are a plus."
    
    extracted = extractor.extract_from_text(sample_title, sample_desc)
    print(f"Title: {sample_title}")
    print(f"Extracted Skills: {extracted}")

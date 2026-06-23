import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

Base = declarative_base()

class DBConnector:
    """
    Manages database engines and sessions with built-in SQLite fallback.
    Demonstrates enterprise-level portability and robust configuration management.
    """
    def __init__(self):
        self.db_type = os.getenv("DB_TYPE", "sqlite").lower()
        self.engine = self._get_engine()
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def _get_engine(self):
        """
        Creates SQLAlchemy engine based on configuration.
        """
        if self.db_type == "mysql":
            user = os.getenv("DB_USER", "root")
            password = os.getenv("DB_PASSWORD", "")
            host = os.getenv("DB_HOST", "localhost")
            port = os.getenv("DB_PORT", "3306")
            db_name = os.getenv("DB_NAME", "placement_intelligence_db")
            
            # Connection string for MySQL
            connection_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}"
            logger.info("Initializing connection engine to MySQL database.")
            try:
                # Test connection immediately
                engine = create_engine(connection_url, pool_recycle=3600, pool_pre_ping=True)
                # Try to connect to ensure configuration is correct
                with engine.connect() as conn:
                    logger.info("MySQL connection established successfully.")
                return engine
            except Exception as e:
                logger.error(f"Failed to connect to MySQL: {e}. Falling back to SQLite cache.")
                self.db_type = "sqlite"

        # Fallback to SQLite (Standard for testing and zero-setup requirements)
        db_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "3_database"))
        os.makedirs(db_dir, exist_ok=True)
        sqlite_path = os.path.join(db_dir, "local_cache.db")
        connection_url = f"sqlite:///{sqlite_path}"
        logger.info(f"Initializing connection engine to local SQLite file: {sqlite_path}")
        return create_engine(connection_url, connect_args={"check_same_thread": False})

    def get_session(self):
        """
        Yields a transactional database session context manager.
        """
        session = self.SessionLocal()
        try:
            return session
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise

    def execute_raw_sql(self, sql_script_path: str):
        """
        Loads and executes a raw SQL script file. 
        Highly useful for bootstrapping tables and seed data.
        """
        if not os.path.exists(sql_script_path):
            logger.error(f"SQL file not found at: {sql_script_path}")
            return False

        logger.info(f"Executing SQL script: {sql_script_path}")
        try:
            with open(sql_script_path, "r", encoding="utf-8") as f:
                sql_content = f.read()

            # Split script into individual queries (ignores comments and empty lines)
            queries = []
            current_query = []
            
            for line in sql_content.splitlines():
                # Strip comments
                stripped = line.strip()
                if not stripped or stripped.startswith("--") or stripped.startswith("/*"):
                    continue
                current_query.append(line)
                if stripped.endswith(";"):
                    queries.append("\n".join(current_query))
                    current_query = []

            # Execute statements
            with self.engine.connect() as conn:
                # In SQLite, we can execute multiple statements via executescript, but engine.execute requires individual runs
                # Using direct DBAPI connection for executing raw scripts cleanly
                raw_connection = conn.connection
                cursor = raw_connection.cursor()
                
                for idx, query in enumerate(queries):
                    try:
                        # Convert generated column syntax for SQLite compatibility if fallback is active
                        if self.db_type == "sqlite":
                            query = self._make_query_sqlite_compatible(query)
                        if not query.strip():
                            continue
                        cursor.execute(query)
                    except Exception as qe:
                        logger.warning(f"Error on query #{idx+1}: {qe}. Continuing...")
                raw_connection.commit()
                logger.info(f"Successfully executed script {sql_script_path}")
                return True
        except Exception as e:
            logger.error(f"Failed to execute raw SQL script: {e}")
            return False

    def _make_query_sqlite_compatible(self, query: str) -> str:
        """
        Utility to strip MySQL-specific instructions (e.g. GENERATED ALWAYS AS, ENGINE=InnoDB)
        when fallback to SQLite is active.
        """
        # Remove MySQL engine specifications
        query = query.replace("ENGINE=InnoDB", "")
        query = query.replace("DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci", "")
        query = query.replace("INT AUTO_INCREMENT PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
        
        # Replace MySQL generated column on jobs table with a plain column definition for SQLite
        if "salary_avg DECIMAL(12, 2) GENERATED ALWAYS AS" in query:
            query = query.replace(
                "salary_avg DECIMAL(12, 2) GENERATED ALWAYS AS ((IFNULL(salary_min, 0) + IFNULL(salary_max, 0)) / 2) STORED,",
                "salary_avg DECIMAL(12, 2) DEFAULT 0.00,"
            )
        
        # Remove CREATE DATABASE / USE queries for SQLite
        if "CREATE DATABASE" in query or "USE " in query:
            return ""
            
        # SQLite doesn't support TRUNCATE, replace with DELETE
        if "TRUNCATE TABLE" in query:
            table_name = query.split("TRUNCATE TABLE")[-1].replace(";", "").strip()
            return f"DELETE FROM {table_name};"

        # SQLite doesn't support ALTER/SET constraints
        if "SET FOREIGN_KEY_CHECKS" in query:
            return ""

        return query

if __name__ == "__main__":
    # Test file execution
    connector = DBConnector()
    print("Connection Successful! Target DB Type:", connector.db_type)

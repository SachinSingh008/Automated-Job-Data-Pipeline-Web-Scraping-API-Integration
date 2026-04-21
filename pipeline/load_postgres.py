import pandas as pd
from sqlalchemy import create_engine, text
import logging
import sys
import os

# Add parent dir to path to import config
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from config.config import Config

logger = logging.getLogger(__name__)

class PostgresLoader:
    def __init__(self):
        self.engine = None
        try:
            self.engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Connected to PostgreSQL successfully.")
            self._create_table()
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")

    def _create_table(self):
        """Creates the generic jobs table if it doesn't already exist."""
        create_sql = text("""
            CREATE TABLE IF NOT EXISTS jobs (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255),
                company VARCHAR(255),
                location VARCHAR(255),
                salary VARCHAR(255),
                skills TEXT,
                source VARCHAR(100),
                scraped_at TIMESTAMP
            );
        """)
        try:
            with self.engine.begin() as conn:
                conn.execute(create_sql)
            logger.info("Table 'jobs' is ready.")
        except Exception as e:
            logger.error(f"Error creating table: {e}")

    def load(self, df: pd.DataFrame):
        if df.empty:
            logger.warning("No data to load into PostgreSQL.")
            return

        if not self.engine:
            logger.warning("PostgreSQL engine is not initialized. Skipping load.")
            return

        try:
            # We rename columns to match our DB schema
            # DataFrame columns from transformer: ['job_title', 'company', 'location', 'salary', 'skills', 'source', 'scraped_at']
            # DB requires 'title' instead of 'job_title'
            db_df = df.rename(columns={'job_title': 'title'})

            # Keep only the columns present in the table
            cols_to_keep = ['title', 'company', 'location', 'salary', 'skills', 'source', 'scraped_at']
            db_df = db_df[[c for c in cols_to_keep if c in db_df.columns]]

            # Load into table using pandas to_sql
            db_df.to_sql('jobs', con=Config.SQLALCHEMY_DATABASE_URI, if_exists='append', index=False, method='multi')
            logger.info(f"Successfully loaded {len(db_df)} structured records into PostgreSQL.")
        except Exception as e:
            logger.error(f"Error loading data to PostgreSQL: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Test connection initialization
    loader = PostgresLoader()

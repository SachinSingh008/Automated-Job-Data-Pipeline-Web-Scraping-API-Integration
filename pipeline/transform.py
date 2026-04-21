import pandas as pd
import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class DataTransformer:
    def __init__(self):
        pass

    def clean_salary(self, salary_str: str) -> str:
        """
        Attempts to standardize salary strings.
        Example: '$100k-$150k' -> '100000-150000'
        If unable to parse, return it cleaned up or 'Not specified'
        """
        if not salary_str or pd.isna(salary_str) or salary_str == "None":
            return "Not specified"
        
        # Remove extra spaces or newlines
        clean_str = salary_str.strip().replace('\n', ' ')
        return clean_str

    def transform(self, raw_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Cleans and transforms raw job data.
        Returns a Pandas DataFrame.
        """
        if not raw_data:
            logger.warning("No data provided to transform.")
            return pd.DataFrame()

        df = pd.DataFrame(raw_data)
        logger.info(f"Transforming dataset with {len(df)} records.")

        # 1. Normalize Column Names (just to be safe)
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

        # 2. Handle missing values
        # We fill NAs in string columns with 'Unknown'
        df.fillna("Unknown", inplace=True)

        # 3. Standardize salary format
        if 'salary' in df.columns:
            df['salary'] = df['salary'].apply(self.clean_salary)

        # 4. Remove Duplicates
        # We assume job_title and company combination makes a row unique 
        # (for simplicity, real world might need more fields)
        before_dedup = len(df)
        df.drop_duplicates(subset=['job_title', 'company'], keep='first', inplace=True)
        after_dedup = len(df)
        logger.info(f"Removed {before_dedup - after_dedup} duplicate records.")

        # Add scraped_at timestamp
        df['scraped_at'] = pd.Timestamp.utcnow()

        logger.info("Data transformation complete.")
        return df

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    dummy_data = [
        {"job_title": "Data Engineer", "company": "Tech Corp", "location": "Remote", "salary": "$100k - $120k", "skills": "Python, SQL"},
        {"job_title": "Data Engineer", "company": "Tech Corp", "location": "Remote", "salary": None, "skills": "Python, SQL"}, # duplicate
        {"job_title": "Data Analyst", "company": "Data Inc ", "location": "NY", "salary": "", "skills": "Excel, Pandas"}
    ]
    transformer = DataTransformer()
    df_clean = transformer.transform(dummy_data)
    print(df_clean)

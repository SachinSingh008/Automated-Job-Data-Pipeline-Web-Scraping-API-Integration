import logging
import sys
import os
import time

# Add parent dir to path to import modules
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from scraper.static_scraper import StaticScraper
from scraper.dynamic_scraper import DynamicScraper
from pipeline.transform import DataTransformer
from pipeline.load_mongo import MongoLoader
from pipeline.load_postgres import PostgresLoader

# Configure logging for the pipeline execution
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def run():
    start_time = time.time()
    logger.info("=========================================")
    logger.info("Starting Automated Job Data Pipeline...")
    logger.info("=========================================")

    all_raw_jobs = []

    # 1. Run Static Scraper
    try:
        logger.info("Running Static Scraper...")
        static_scraper = StaticScraper()
        static_jobs = static_scraper.scrape()
        all_raw_jobs.extend(static_jobs)
    except Exception as e:
        logger.error(f"Static scraper failed: {e}")

    # 2. Run Dynamic Scraper
    try:
        logger.info("Running Dynamic Scraper...")
        dynamic_scraper = DynamicScraper()
        dynamic_jobs = dynamic_scraper.scrape()
        all_raw_jobs.extend(dynamic_jobs)
    except Exception as e:
        logger.error(f"Dynamic scraper failed: {e}")

    if not all_raw_jobs:
        logger.warning("No jobs were scraped. Pipeline ending early.")
        return

    logger.info(f"Total jobs scraped: {len(all_raw_jobs)}")

    # 3. Load Raw Data to MongoDB
    try:
        logger.info("Loading raw data to MongoDB...")
        mongo_loader = MongoLoader()
        mongo_loader.load(all_raw_jobs)
    except Exception as e:
        logger.error(f"MongoDB loading failed: {e}")

    # 4. Transform Data
    clean_df = None
    try:
        logger.info("Transforming and cleaning data...")
        transformer = DataTransformer()
        clean_df = transformer.transform(all_raw_jobs)
    except Exception as e:
        logger.error(f"Data transformation failed: {e}")

    # 5. Load Clean Data to PostgreSQL
    if clean_df is not None and not clean_df.empty:
        try:
            logger.info("Loading structured data to PostgreSQL...")
            pg_loader = PostgresLoader()
            pg_loader.load(clean_df)
        except Exception as e:
            logger.error(f"PostgreSQL loading failed: {e}")
    else:
        logger.warning("Clean dataframe was empty. Skipping PostgreSQL load.")

    elapsed = time.time() - start_time
    logger.info(f"Pipeline finished successfully in {elapsed:.2f} seconds.")
    logger.info("=========================================")

if __name__ == "__main__":
    run()

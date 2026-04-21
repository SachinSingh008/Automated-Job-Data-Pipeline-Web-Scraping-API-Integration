import pymongo
import logging
from typing import List, Dict, Any
import sys
import os

# Add parent dir to path to import config
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from config.config import Config

logger = logging.getLogger(__name__)

class MongoLoader:
    def __init__(self):
        try:
            self.client = pymongo.MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
            self.db = self.client[Config.MONGO_DB]
            self.collection = self.db[Config.MONGO_COLLECTION]
            # Simple ping to test connectivity
            self.client.admin.command('ping')
            logger.info("Connected to MongoDB successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self.client = None

    def load(self, raw_data: List[Dict[str, Any]]):
        if not raw_data:
            logger.warning("No raw data to load into MongoDB.")
            return

        if not self.client:
            logger.warning("MongoDB client is not connected. Skipping load.")
            return

        try:
            # We insert many documents at once.
            # Real application may want to upsert to avoid duplicates here too,
            # but instructions say store "raw/unstructured data", so append is fine.
            result = self.collection.insert_many(raw_data)
            logger.info(f"Successfully loaded {len(result.inserted_ids)} raw documents into MongoDB.")
        except Exception as e:
            logger.error(f"Error loading data to MongoDB: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    loader = MongoLoader()
    # Simple test data
    loader.load([{"test": "document", "source": "manual_run"}])

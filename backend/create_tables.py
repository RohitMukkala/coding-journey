from sqlalchemy import create_engine
from models import Base, User, CodingProfile  # Import the actual models
from database import DATABASE_URL
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db(max_retries=3, retry_delay=5):
    for attempt in range(max_retries):
        try:
            engine = create_engine(
                DATABASE_URL,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=1800,
                connect_args={
                    "application_name": "coding_journey_app",
                    "keepalives": 1,
                    "keepalives_idle": 30,
                    "keepalives_interval": 10,
                    "keepalives_count": 5
                }
            )
            
            # Test connection
            with engine.connect() as connection:
                logger.info("Successfully connected to the database")
            
            # Drop all tables
            Base.metadata.drop_all(bind=engine)
            logger.info("Successfully dropped all tables")
            
            # Create all tables
            Base.metadata.create_all(bind=engine)
            logger.info("Successfully created all tables")
            
            return True
            
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Max retries reached. Database initialization failed.")
                raise

if __name__ == "__main__":
    init_db() 
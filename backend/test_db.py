from sqlalchemy import create_engine, inspect
from database import DATABASE_URL
import psycopg2
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_connection(max_retries=3, retry_delay=5):
    logger.info("Testing database connection...")
    
    for attempt in range(max_retries):
        try:
            # Create connection parameters with keepalive settings
            conn = psycopg2.connect(
                DATABASE_URL,
                keepalives=1,
                keepalives_idle=30,
                keepalives_interval=10,
                keepalives_count=5,
                application_name='coding_journey_app'
            )
            
            cur = conn.cursor()
            
            # List all tables
            cur.execute("""
                SELECT table_name, column_name, data_type 
                FROM information_schema.columns
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position;
            """)
            
            logger.info("\nCurrent database structure:")
            current_table = None
            for table, column, dtype in cur.fetchall():
                if table != current_table:
                    logger.info(f"\n{table}:")
                    current_table = table
                logger.info(f"  - {column} ({dtype})")
                
            cur.close()
            conn.close()
            logger.info("\nDatabase connection successful!")
            return True
            
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Max retries reached. Database connection test failed.")
                raise

if __name__ == "__main__":
    test_connection() 
from sqlalchemy import create_engine, text
from database import DATABASE_URL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_coding_profiles_table():
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as connection:
            # Drop the existing coding_profiles table
            connection.execute(text("DROP TABLE IF EXISTS coding_profiles CASCADE"))
            connection.commit()
            
            # Create the new coding_profiles table with updated schema
            connection.execute(text("""
                CREATE TABLE coding_profiles (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    platform VARCHAR NOT NULL,
                    username VARCHAR NOT NULL,
                    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    
                    -- GitHub specific fields
                    total_contributions INTEGER,
                    current_streak INTEGER,
                    longest_streak INTEGER,
                    total_stars INTEGER,
                    total_forks INTEGER,
                    languages JSONB,
                    
                    -- LeetCode specific fields
                    total_problems_solved INTEGER,
                    easy_solved INTEGER,
                    medium_solved INTEGER,
                    hard_solved INTEGER,
                    easy_percentage FLOAT,
                    medium_percentage FLOAT,
                    hard_percentage FLOAT,
                    
                    -- CodeChef specific fields
                    current_rating INTEGER,
                    highest_rating INTEGER,
                    global_rank INTEGER,
                    country_rank INTEGER,
                    stars VARCHAR,
                    
                    -- CodeForces specific fields
                    codeforces_rating INTEGER,
                    codeforces_max_rating INTEGER,
                    problems_solved_count INTEGER,
                    contest_rating INTEGER,
                    
                    UNIQUE(user_id, platform)
                )
            """))
            
            # Create index for faster lookups
            connection.execute(text(
                "CREATE INDEX idx_coding_profiles_user_platform ON coding_profiles(user_id, platform)"
            ))
            
            connection.commit()
            logger.info("Successfully updated coding_profiles table schema")
            
    except Exception as e:
        logger.error(f"Error updating coding_profiles table: {str(e)}")
        raise

if __name__ == "__main__":
    update_coding_profiles_table() 
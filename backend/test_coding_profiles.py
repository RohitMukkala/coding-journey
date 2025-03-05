from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database import DATABASE_URL
from models import CodingProfile
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_table_contents():
    """Check coding_profiles table contents using raw SQL."""
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as connection:
            # Check if table exists
            result = connection.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'coding_profiles'
                );
            """))
            exists = result.scalar()
            
            if not exists:
                logger.error("coding_profiles table does not exist!")
                return
            
            # Get table structure
            logger.info("\nTable Structure:")
            result = connection.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'coding_profiles'
                ORDER BY ordinal_position;
            """))
            for row in result:
                logger.info(f"Column: {row[0]}, Type: {row[1]}, Nullable: {row[2]}")
            
            # Get row count
            result = connection.execute(text("SELECT COUNT(*) FROM coding_profiles;"))
            count = result.scalar()
            logger.info(f"\nTotal rows in coding_profiles: {count}")
            
            # Get sample data
            logger.info("\nSample data from coding_profiles:")
            result = connection.execute(text("""
                SELECT id, user_id, platform, username, last_updated 
                FROM coding_profiles 
                LIMIT 5;
            """))
            for row in result:
                logger.info(f"ID: {row[0]}, User ID: {row[1]}, Platform: {row[2]}, Username: {row[3]}, Last Updated: {row[4]}")
                
            # Get platform-specific data samples
            for platform in ['github', 'leetcode', 'codechef', 'codeforces']:
                logger.info(f"\nLatest {platform} profile data:")
                if platform == 'github':
                    result = connection.execute(text(f"""
                        SELECT total_contributions, current_streak, total_stars, languages
                        FROM coding_profiles
                        WHERE platform = '{platform}'
                        ORDER BY last_updated DESC
                        LIMIT 1;
                    """))
                elif platform == 'leetcode':
                    result = connection.execute(text(f"""
                        SELECT total_problems_solved, easy_solved, medium_solved, hard_solved
                        FROM coding_profiles
                        WHERE platform = '{platform}'
                        ORDER BY last_updated DESC
                        LIMIT 1;
                    """))
                elif platform == 'codechef':
                    result = connection.execute(text(f"""
                        SELECT current_rating, highest_rating, global_rank, stars
                        FROM coding_profiles
                        WHERE platform = '{platform}'
                        ORDER BY last_updated DESC
                        LIMIT 1;
                    """))
                else:  # codeforces
                    result = connection.execute(text(f"""
                        SELECT codeforces_rating, codeforces_max_rating, problems_solved_count
                        FROM coding_profiles
                        WHERE platform = '{platform}'
                        ORDER BY last_updated DESC
                        LIMIT 1;
                    """))
                
                row = result.fetchone()
                if row:
                    logger.info(f"Data: {dict(zip(result.keys(), row))}")
                else:
                    logger.info(f"No {platform} profiles found")
                    
    except Exception as e:
        logger.error(f"Error checking table contents: {str(e)}")

def test_coding_profiles():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Query all coding profiles
        profiles = session.query(CodingProfile).all()
        
        if not profiles:
            logger.info("No coding profiles found in the database.")
            return
        
        logger.info(f"Found {len(profiles)} coding profiles")
        
        # Print details for each profile
        for profile in profiles:
            logger.info("\n" + "="*50)
            logger.info(f"Profile ID: {profile.id}")
            logger.info(f"User ID: {profile.user_id}")
            logger.info(f"Platform: {profile.platform}")
            logger.info(f"Username: {profile.username}")
            logger.info(f"Last Updated: {profile.last_updated}")
            
            if profile.platform == "github":
                logger.info("\nGitHub Stats:")
                logger.info(f"Total Contributions: {profile.total_contributions}")
                logger.info(f"Current Streak: {profile.current_streak}")
                logger.info(f"Longest Streak: {profile.longest_streak}")
                logger.info(f"Total Stars: {profile.total_stars}")
                logger.info(f"Total Forks: {profile.total_forks}")
                logger.info(f"Languages: {profile.languages}")
                
            elif profile.platform == "leetcode":
                logger.info("\nLeetCode Stats:")
                logger.info(f"Total Problems Solved: {profile.total_problems_solved}")
                logger.info(f"Easy Solved: {profile.easy_solved}")
                logger.info(f"Medium Solved: {profile.medium_solved}")
                logger.info(f"Hard Solved: {profile.hard_solved}")
                logger.info(f"Easy %: {profile.easy_percentage}")
                logger.info(f"Medium %: {profile.medium_percentage}")
                logger.info(f"Hard %: {profile.hard_percentage}")
                
            elif profile.platform == "codechef":
                logger.info("\nCodeChef Stats:")
                logger.info(f"Current Rating: {profile.current_rating}")
                logger.info(f"Highest Rating: {profile.highest_rating}")
                logger.info(f"Global Rank: {profile.global_rank}")
                logger.info(f"Country Rank: {profile.country_rank}")
                logger.info(f"Stars: {profile.stars}")
                
            elif profile.platform == "codeforces":
                logger.info("\nCodeForces Stats:")
                logger.info(f"Current Rating: {profile.codeforces_rating}")
                logger.info(f"Max Rating: {profile.codeforces_max_rating}")
                logger.info(f"Problems Solved: {profile.problems_solved_count}")
                logger.info(f"Contest Rating: {profile.contest_rating}")
            
            logger.info("="*50)
            
    except Exception as e:
        logger.error(f"Error querying coding profiles: {str(e)}")
    finally:
        session.close()

if __name__ == "__main__":
    logger.info("Checking table contents...")
    check_table_contents()
    logger.info("\nChecking profiles using ORM...")
    test_coding_profiles() 
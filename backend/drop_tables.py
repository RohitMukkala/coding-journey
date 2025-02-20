import psycopg2
from database import DATABASE_URL

def drop_all_tables():
    print("Connecting to database...")
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cur = conn.cursor()
    
    # Drop all tables in public schema
    print("Dropping all tables...")
    cur.execute("""
        DO $$ DECLARE
            r RECORD;
        BEGIN
            FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
            END LOOP;
        END $$;
    """)
    
    print("All tables dropped successfully!")
    cur.close()
    conn.close()

if __name__ == "__main__":
    drop_all_tables() 
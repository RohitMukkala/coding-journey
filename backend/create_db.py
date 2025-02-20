from database import engine
from models import Base

# Create the tables in the database
Base.metadata.create_all(bind=engine)

#python create_db.py
#Run the script to create tables in your Supabase PostgreSQL database:
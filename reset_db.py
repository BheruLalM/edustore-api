import os
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env.local")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not found in .env.local")
    exit(1)

def reset_database():
    print(f"🔄 Connecting to database...")
    engine = create_engine(DATABASE_URL)
    
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    
    if not table_names:
        print("✅ Database is already empty (no tables found).")
        return

    # Filter out alembic_version table to preserve migrations
    tables_to_truncate = [t for t in table_names if t != 'alembic_version']
    
    if not tables_to_truncate:
        print("✅ No data tables found (only migration tables exist).")
        return

    print(f"📝 Found {len(tables_to_truncate)} tables to clear: {', '.join(tables_to_truncate)}")
    
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            # PostgreSQL specific truncate with CASCADE
            truncate_query = f"TRUNCATE TABLE {', '.join(tables_to_truncate)} CASCADE;"
            connection.execute(text(truncate_query))
            transaction.commit()
            print("✨ Successfully cleared all data from the database!")
        except Exception as e:
            transaction.rollback()
            print(f"❌ Failed to clear database: {e}")
            raise e

if __name__ == "__main__":
    reset_database()

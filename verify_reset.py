import os
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env.local")

DATABASE_URL = os.getenv("DATABASE_URL")

def verify_empty():
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    
    with engine.connect() as connection:
        for table in table_names:
            if table == 'alembic_version':
                continue
            count = connection.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"Table {table}: {count} rows")

if __name__ == "__main__":
    verify_empty()

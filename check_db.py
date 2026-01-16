from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL")
engine = create_engine(db_url)

with engine.connect() as conn:
    try:
        # Try a raw SQL insert
        res = conn.execute(text("""
            INSERT INTO documents (user_id, title, doc_type, content, visibility, created_at)
            VALUES (1, 'Test Title', 'post', 'Test Content', 'public', now())
            RETURNING id
        """))
        conn.commit()
        print(f"Success! Inserted post with id: {res.fetchone()[0]}")
    except Exception as e:
        print(f"Raw insert failed: {e}")

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# --- UPDATE: Connection Pooling Settings ---
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # Har query se pehle connection check karega (SSL fix)
    pool_recycle=300,     # Har 5 minute baad connection refresh karega
    pool_size=5,          # Maximum 5 active connections rakhega
    max_overflow=10       # Zarurat parne par 10 mazeed connections bana sakega
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Purani files ko fix karne wala logic
def fix_missing_dates():
    try:
        with engine.connect() as connection:
            connection.execute(text("UPDATE documents SET upload_date = NOW() WHERE upload_date IS NULL"))
            connection.commit()
            print("✅ Database migration: Missing dates fixed!")
    except Exception as e:
        # Table na bani ho ya connection issue ho toh skip
        print(f"⚠️ Migration skipped or table not found: {e}")

# Migration ko run karein
fix_missing_dates()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
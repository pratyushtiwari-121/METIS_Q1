from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

# Ensure sqlite directory exists if a path is provided
if settings.DATABASE_URL.startswith("sqlite:///"):
    db_path_str = settings.DATABASE_URL.replace("sqlite:///", "")
    if db_path_str and db_path_str != ":memory:":
        Path(db_path_str).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

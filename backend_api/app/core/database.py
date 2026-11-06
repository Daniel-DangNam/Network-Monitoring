from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging
import os

logger = logging.getLogger(__name__)

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Cố gắng kết nối PostgreSQL; nếu không khả dụng thì fallback sang SQLite để hệ thống không bị crash
try:
    if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
        engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
        # Thử kết nối test
        with engine.connect() as conn:
            pass
except Exception as e:
    logger.warning(f"Không thể kết nối cơ sở dữ liệu chính ({SQLALCHEMY_DATABASE_URL}): {e}. Chuyển sang SQLite local.")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_file = os.path.join(base_dir, "network_db.sqlite3")
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_file}"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

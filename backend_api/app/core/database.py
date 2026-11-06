from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging

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
    SQLALCHEMY_DATABASE_URL = "sqlite:///./network_db.sqlite3"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app.core.database import Base

class ClassificationHistory(Base):
    __tablename__ = "classification_history"

    id = Column(Integer, primary_key=True, index=True)
    log_timestamp = Column(DateTime, default=datetime.utcnow)
    ai_prediction = Column(String)
    packet_count = Column(Integer)
    websites = Column(JSONB)

# Bảng mới để lưu tài khoản người dùng
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
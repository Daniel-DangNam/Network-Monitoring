from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class LogPayload(BaseModel):
    timestamp: Optional[str] = None
    client_ip: Optional[str] = "Local"
    ai_prediction: str
    packet_count: int
    websites: List[str] = []

class ClassificationRecord(BaseModel):
    id: int
    log_timestamp: datetime
    client_ip: Optional[str] = "Local"
    ai_prediction: str
    packet_count: int
    websites: List[str] = []

    class Config:
        from_attributes = True

class HistoryResponse(BaseModel):
    total: int
    data: List[ClassificationRecord]

class RealtimeLogItem(BaseModel):
    id: int
    client_ip: Optional[str] = "Local"
    ai_prediction: str
    packet_count: int
    websites: List[str]
    timestamp: str


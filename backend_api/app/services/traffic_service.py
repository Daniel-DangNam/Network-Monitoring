import csv
import io
from typing import List
from sqlalchemy.orm import Session
from app.models.traffic import ClassificationHistory
from app.schemas.traffic import LogPayload, RealtimeLogItem
from app.utils.socket_manager import manager

class TrafficService:
    @staticmethod
    def get_history(db: Session, limit: int = 1000) -> List[ClassificationHistory]:
        return db.query(ClassificationHistory).order_by(ClassificationHistory.id.desc()).limit(limit).all()

    @staticmethod
    async def save_log(db: Session, payload: LogPayload) -> ClassificationHistory:
        record = ClassificationHistory(
            ai_prediction=payload.ai_prediction,
            packet_count=payload.packet_count,
            websites=payload.websites
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        realtime_data = {
            "id": record.id,
            "ai_prediction": record.ai_prediction,
            "packet_count": record.packet_count,
            "websites": record.websites or [],
            "timestamp": str(record.log_timestamp)
        }
        await manager.broadcast(realtime_data)
        return record

    @staticmethod
    def generate_csv_report(records: List[ClassificationHistory]) -> io.StringIO:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Timestamp", "Packet Count", "AI Prediction Label", "Destination / Websites"])

        for record in records:
            websites_str = ", ".join(record.websites) if isinstance(record.websites, list) else str(record.websites or "")
            writer.writerow([
                record.id,
                str(record.log_timestamp),
                record.packet_count,
                record.ai_prediction,
                websites_str
            ])
        output.seek(0)
        return output

traffic_service = TrafficService()


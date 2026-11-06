from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.schemas.traffic import LogPayload, HistoryResponse
from app.services.traffic_service import traffic_service
from app.models.user import User

router = APIRouter()

@router.get("/history", response_model=HistoryResponse)
def get_history(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    records = traffic_service.get_history(db)
    return {"total": len(records), "data": records}

@router.post("/save-log")
async def save_log(payload: LogPayload, db: Session = Depends(get_db)):
    record = await traffic_service.save_log(db, payload)
    return {"status": "success", "history_id": record.id}

@router.get("/export/csv")
def export_history_csv(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    records = traffic_service.get_history(db)
    output = traffic_service.generate_csv_report(records)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=network_traffic_report.csv"}
    )


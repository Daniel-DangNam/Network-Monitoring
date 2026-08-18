from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

import subprocess
import os
import signal

# Import từ các module trong kiến trúc mới
from app.core import database, auth
from app.models import models
from app.utils.socket_manager import manager

router = APIRouter()

# Biến toàn cục lưu trữ tiến trình Network Agent đang chạy ngầm
agent_process = None

# Khung chuẩn hóa dữ liệu JSON (Có thể tách ra file app/schemas/schemas.py nếu dự án lớn hơn)
class LogPayload(BaseModel):
    timestamp: str
    ai_prediction: str
    packet_count: int
    websites: List[str]

class UserCreate(BaseModel):
    username: str
    password: str

# --- LUỒNG BẢO MẬT (AUTH) ---

@router.post("/api/v1/register")
def register_user(user: UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Tài khoản đã tồn tại")
    
    hashed_pwd = auth.get_password_hash(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Tạo tài khoản thành công!"}

@router.post("/api/v1/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sai tài khoản hoặc mật khẩu",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = auth.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- LUỒNG ĐIỀU KHIỂN NETWORK AGENT ---

@router.post("/api/v1/start-agent")
def start_agent():
    global agent_process
    if agent_process is not None and agent_process.poll() is None:
        return {"status": "info", "message": "Network Agent đang được chạy rồi!"}

    try:
        python_exec = "/home/namdang/Desktop/Network_Monitoring/venv/bin/python"
        script_path = "/home/namdang/Desktop/Network_Monitoring/network_agent/live_pipeline.py"
        cwd_path = "/home/namdang/Desktop/Network_Monitoring/network_agent"

        agent_process = subprocess.Popen(
            [python_exec, script_path],
            cwd=cwd_path,
            preexec_fn=os.setsid 
        )
        return {"status": "success", "message": "Đã khởi động AI Network Agent thành công!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi khởi động: {str(e)}")

@router.post("/api/v1/stop-agent")
def stop_agent():
    global agent_process
    if agent_process is None or agent_process.poll() is not None:
        return {"status": "info", "message": "Network Agent hiện không chạy."}

    try:
        os.killpg(os.getpgid(agent_process.pid), signal.SIGTERM)
        agent_process = None
        return {"status": "success", "message": "Đã dừng AI Network Agent an toàn!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi dừng: {str(e)}")


# --- LUỒNG NGHIỆP VỤ (BUSINESS LOGIC) ---

@router.get("/api/v1/history")
def get_history(
    db: Session = Depends(database.get_db), 
    token: str = Depends(auth.oauth2_scheme)
):
    records = db.query(models.ClassificationHistory).order_by(models.ClassificationHistory.id.desc()).all()
    return {"total": len(records), "data": records}

@router.post("/api/v1/save-log")
async def save_log(payload: LogPayload, db: Session = Depends(database.get_db)):
    history_record = models.ClassificationHistory(
        ai_prediction=payload.ai_prediction,
        packet_count=payload.packet_count,
        websites=payload.websites
    )
    db.add(history_record)
    db.commit()
    db.refresh(history_record)
    
    realtime_data = {
        "id": history_record.id,
        "ai_prediction": history_record.ai_prediction,
        "packet_count": history_record.packet_count,
        "websites": history_record.websites,
        "timestamp": str(history_record.log_timestamp)
    }
    await manager.broadcast(realtime_data)

    return {"status": "success", "history_id": history_record.id}

# --- CỔNG KẾT NỐI REAL-TIME (WEBSOCKETS) ---

@router.websocket("/ws/realtime")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Nhận được tín hiệu từ Client: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
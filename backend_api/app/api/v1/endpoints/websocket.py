from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.utils.socket_manager import manager

router = APIRouter()

@router.websocket("/ws/realtime")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Xử lý ping/pong từ frontend
    except WebSocketDisconnect:
        manager.disconnect(websocket)


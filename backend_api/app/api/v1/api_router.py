from fastapi import APIRouter
from app.api.v1.endpoints import auth, traffic, agent, pcap, websocket

api_router = APIRouter()

# Đăng ký các endpoints theo chuẩn RESTful
api_router.include_router(auth.router, tags=["Authentication"])
api_router.include_router(traffic.router, tags=["Traffic & Logs"])
api_router.include_router(agent.router, tags=["Network Agent Control"])
api_router.include_router(pcap.router, prefix="/pcap", tags=["PCAP Processing"])
api_router.include_router(websocket.router, tags=["WebSocket Realtime"])


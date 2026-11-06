from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
import app.models.user
import app.models.traffic
from app.models.user import User
from app.core.security import get_password_hash
from app.api.v1.api_router import api_router
from app.utils.socket_manager import manager

# Tự động tạo các bảng cơ sở dữ liệu nếu chưa tồn tại
Base.metadata.create_all(bind=engine)

# Tự động khởi tạo tài khoản quản trị viên mặc định (admin / 123456) nếu chưa có
def init_default_admin():
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            hashed = get_password_hash("123456")
            admin_user = User(username="admin", hashed_password=hashed, is_active=True)
            db.add(admin_user)
            db.commit()
    except Exception:
        pass
    finally:
        db.close()

init_default_admin()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API giám sát & phân loại lưu lượng mạng thời gian thực sử dụng Online Machine Learning (ĐATN)"
)

# Cấu hình CORS đa môi trường
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# Nhúng Router API v1
app.include_router(api_router, prefix=settings.API_V1_STR)

# Đường dẫn tương thích ngược trực tiếp cho WebSocket: ws://localhost:8000/ws/realtime
@app.websocket("/ws/realtime")
async def root_websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        manager.disconnect(websocket)

# Endpoint kiểm tra trạng thái sức khỏe hệ thống
@app.get("/")
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION
    }

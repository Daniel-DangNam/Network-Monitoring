from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import từ các module con
from app.api.routes import router as api_router
from app.core import database
from app.models import models

# Khởi tạo bảng trong CSDL
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Network AI Backend")

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], # Cấp phép cho cổng của ReactJS
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# Nhúng toàn bộ Routes vào ứng dụng
app.include_router(api_router)
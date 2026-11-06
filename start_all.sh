#!/bin/bash

# Thư mục gốc dự án
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

echo "=================================================="
echo " 🚀 KHỞI CHẠY TOÀN BỘ HỆ THỐNG NETWORK MONITORING 🚀"
echo "=================================================="

# Hàm dọn dẹp khi bấm Ctrl+C
cleanup() {
    echo ""
    echo "=================================================="
    echo " 🛑 Đang tắt toàn bộ hệ thống..."
    echo "=================================================="
    if [ -n "$BACKEND_PID" ]; then
        kill "$BACKEND_PID" 2>/dev/null || true
    fi
    if [ -n "$FRONTEND_PID" ]; then
        kill "$FRONTEND_PID" 2>/dev/null || true
    fi
    pkill -f "live_pipeline.py" 2>/dev/null || true
    echo "✅ Đã tắt an toàn toàn bộ dịch vụ!"
    exit 0
}

trap cleanup SIGINT SIGTERM

# 1. Khởi chạy Backend (Port 8000)
echo "1. Đang khởi động Backend FastAPI (Port 8000)..."
cd "$ROOT_DIR/backend_api"
if [ -d "../venv" ]; then
    source ../venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
sleep 2

# 2. Khởi chạy Frontend Dashboard (Port 5173)
echo "2. Đang khởi động React Dashboard (Port 5173)..."
cd "$ROOT_DIR/frontend-dashboard"
if [ ! -d "node_modules" ]; then
    echo "Đang cài đặt thư viện npm..."
    npm install
fi
npm run dev -- --host &
FRONTEND_PID=$!
sleep 2

echo ""
echo "=================================================="
echo " 🎉 TẤT CẢ DỊCH VỤ ĐÃ SẴN SÀNG!"
echo " 👉 Mở trình duyệt truy cập: http://localhost:5173"
echo " 👉 Tài liệu API Swagger:   http://localhost:8000/docs"
echo " 💡 Bạn chỉ cần vào Dashboard bấm 'Start Sniffing' để bắt gói tin!"
echo " 🛑 Khi muốn dừng toàn bộ: Bấm [Ctrl + C] tại Terminal này."
echo "=================================================="

# Giữ script luôn chạy và lắng nghe Ctrl+C
wait


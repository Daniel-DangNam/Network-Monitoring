#!/bin/bash

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

echo "=================================================="
echo " 🚀 KHỞI CHẠY HỆ THỐNG NETWORK MONITORING DASHBOARD 🚀"
echo " (Chế độ chờ: Nhấn 'Start Sniffing' trên Web để bắt)"
echo "=================================================="

# 1. Yêu cầu quyền sudo một lần để phân quyền RAW socket cho Python
echo "🔑 Phân quyền card mạng cho Python (để bấm Start/Stop trực tiếp trên Web):"
sudo -v

# Kích hoạt virtualenv để lấy đúng binary Python
if [ -d "$ROOT_DIR/venv" ]; then
    source "$ROOT_DIR/venv/bin/activate"
elif [ -d "$ROOT_DIR/backend_api/venv" ]; then
    source "$ROOT_DIR/backend_api/venv/bin/activate"
fi
PYTHON_BIN="$(which python3)"
PYTHON_REAL="$(readlink -f "$PYTHON_BIN")"

# Cấp quyền CAP_NET_RAW cho Python để Backend có thể start/stop agent mà không bị văng
echo "Phân quyền CAP_NET_RAW cho: $PYTHON_REAL"
sudo setcap cap_net_raw,cap_net_admin=eip "$PYTHON_REAL" 2>/dev/null || true

# Dọn dẹp các tiến trình agent cũ nếu có để trạng thái ban đầu là STANDBY sạch sẽ
pkill -f "live_pipeline.py" 2>/dev/null || true

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

trap cleanup SIGINT SIGTERM EXIT

# 2. Khởi chạy Backend (Port 8000)
echo "1. Đang khởi động Backend FastAPI (Port 8000)..."
cd "$ROOT_DIR/backend_api"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
sleep 2

# 3. Khởi chạy Frontend Dashboard (Port 5173)
echo "2. Đang khởi động React Dashboard (Port 5173)..."
cd "$ROOT_DIR/frontend-dashboard"
if ! command -v npm &> /dev/null; then
    echo "⚠️ Đang cài đặt nodejs và npm..."
    sudo apt-get update && sudo apt-get install -y nodejs npm
fi
if [ ! -d "node_modules" ]; then
    echo "Đang cài đặt thư viện npm..."
    npm install
fi
npm run dev -- --host &
FRONTEND_PID=$!
sleep 2

echo ""
echo "=================================================="
echo " 🎉 HỆ THỐNG ĐÃ SẴN SÀNG Ở CHẾ ĐỘ CHỜ (STANDBY)!"
echo " 👉 Mở trình duyệt truy cập: http://localhost:5173"
echo " 🔘 Nhấn nút 'Start Sniffing' trên Web để BẮT ĐẦU"
echo " 🔘 Nhấn nút 'Stop Sniffing' trên Web để TẠM DỪNG"
echo " 🛑 Khi muốn tắt máy chủ: Bấm [Ctrl + C] tại Terminal này."
echo "=================================================="

# Giữ script luôn chạy và lắng nghe Ctrl+C
wait

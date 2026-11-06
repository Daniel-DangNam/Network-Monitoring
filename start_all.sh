#!/bin/bash

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

echo "=================================================="
echo " 🚀 KHỞI CHẠY TOÀN BỘ HỆ THỐNG NETWORK MONITORING 🚀"
echo " (Bao gồm: Backend + Frontend + AI Sniffer Agent)"
echo "=================================================="

# 1. Yêu cầu quyền sudo một lần ngay từ đầu để Agent có quyền bắt gói tin trên card mạng
echo "🔑 Cấp quyền root cho Network Agent:"
sudo -v

# Tự động giữ quyền sudo trong lúc script đang chạy
while true; do sudo -n true; sleep 50; kill -0 "$$" || exit; done 2>/dev/null &
SUDO_KEEP_PID=$!

# Hàm dọn dẹp khi bấm Ctrl+C
cleanup() {
    echo ""
    echo "=================================================="
    echo " 🛑 Đang tắt toàn bộ hệ thống..."
    echo "=================================================="
    if [ -n "$SUDO_KEEP_PID" ]; then
        kill "$SUDO_KEEP_PID" 2>/dev/null || true
    fi
    if [ -n "$AGENT_PID" ]; then
        sudo kill "$AGENT_PID" 2>/dev/null || true
    fi
    if [ -n "$BACKEND_PID" ]; then
        kill "$BACKEND_PID" 2>/dev/null || true
    fi
    if [ -n "$FRONTEND_PID" ]; then
        kill "$FRONTEND_PID" 2>/dev/null || true
    fi
    sudo pkill -f "live_pipeline.py" 2>/dev/null || true
    echo "✅ Đã tắt an toàn toàn bộ 3 dịch vụ!"
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# 2. Khởi chạy Backend (Port 8000)
echo "1. Đang khởi động Backend FastAPI (Port 8000)..."
cd "$ROOT_DIR/backend_api"
if [ -d "../venv" ]; then
    source ../venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi
PYTHON_BIN="$(which python3)"
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

# 4. Khởi chạy AI Network Sniffer Agent với quyền root
echo "3. Đang khởi động AI Network Sniffer Agent (Card mạng ens33)..."
cd "$ROOT_DIR/network_agent"
sudo -E "$PYTHON_BIN" -u live_pipeline.py &
AGENT_PID=$!
sleep 2

echo ""
echo "=================================================="
echo " 🎉 TẤT CẢ 3 DỊCH VỤ ĐÃ HOẠT ĐỘNG HOÀN HẢO!"
echo " 👉 Mở trình duyệt truy cập: http://localhost:5173"
echo " 📡 Agent đã TỰ ĐỘNG BẮT GÓI TIN trên card mạng!"
echo " 🛑 Khi muốn dừng toàn bộ: Bấm [Ctrl + C] tại Terminal này."
echo "=================================================="

# Giữ script luôn chạy và lắng nghe Ctrl+C
wait

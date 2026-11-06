#!/bin/bash
set -e
echo "=================================================="
echo " [SETUP] Khởi tạo môi trường Ubuntu / Linux       "
echo "=================================================="

# 1. Cài đặt các gói hệ thống cần thiết (libpcap, python3-venv, tcpdump)
echo "1. Cài đặt thư viện hệ thống cần thiết..."
sudo apt-get update
sudo apt-get install -y python3-dev python3-venv python3-pip libpcap-dev tcpdump curl

# 2. Tạo môi trường ảo
echo "2. Khởi tạo Python Virtual Environment..."
cd "$(dirname "$0")"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# 3. Cài đặt thư viện backend
echo "3. Cài đặt thư viện Backend..."
pip install --upgrade pip
pip install fastapi uvicorn passlib pyjwt python-multipart sqlalchemy bcrypt requests

# 4. Cài đặt thư viện AI Agent
echo "4. Cài đặt thư viện Network Agent..."
pip install scapy pandas numpy torch torchvision cicflowmeter

# 5. Phân quyền chạy raw socket cho Python (không cần sudo sau này)
echo "5. Phân quyền CAP_NET_RAW cho Python..."
PYTHON_BIN="$(readlink -f $(which python3))"
sudo setcap cap_net_raw,cap_net_admin=eip "$PYTHON_BIN" || true

# 6. Cấp quyền thực thi cho các file .sh
chmod +x run_backend.sh run_frontend.sh run_agent.sh setup_ubuntu.sh || true

echo "=================================================="
echo " Cài đặt hoàn tất! Bạn có thể chạy:               "
echo " - ./run_backend.sh                               "
echo " - ./run_frontend.sh                              "
echo " - ./run_agent.sh                                 "
echo "=================================================="


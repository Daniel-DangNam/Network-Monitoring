#!/bin/bash
set -e
echo "=================================================="
echo " [SETUP] Khởi tạo môi trường Ubuntu / Linux       "
echo "=================================================="

# 1. Cài đặt các gói hệ thống cần thiết (libpcap, python3-venv, tcpdump, postgresql, nodejs, npm)
echo "1. Cài đặt thư viện hệ thống cần thiết..."
sudo apt-get update
sudo apt-get install -y python3-dev python3-venv python3-pip libpcap-dev tcpdump curl postgresql postgresql-contrib libpq-dev nodejs npm

# Khởi động dịch vụ PostgreSQL
sudo systemctl enable postgresql || true
sudo systemctl start postgresql || true

# Tự động tạo user và database cho dự án nếu chưa có
echo "Khởi tạo cơ sở dữ liệu PostgreSQL (network_db)..."
sudo -u postgres psql -tc "SELECT 1 FROM pg_user WHERE usename = 'hoanganh'" | grep -q 1 || sudo -u postgres psql -c "CREATE USER hoanganh WITH PASSWORD '123456';" || true
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname = 'network_db'" | grep -q 1 || sudo -u postgres psql -c "CREATE DATABASE network_db OWNER hoanganh;" || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE network_db TO hoanganh;" || true

# 2. Tạo môi trường ảo
echo "2. Khởi tạo Python Virtual Environment..."
cd "$(dirname "$0")"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# 3. Cài đặt thư viện backend (kèm psycopg2 cho PostgreSQL và websockets cho realtime)
echo "3. Cài đặt thư viện Backend..."
pip install --upgrade pip
pip install fastapi "uvicorn[standard]" websockets passlib pyjwt python-multipart sqlalchemy bcrypt requests psycopg2-binary

# 4. Cài đặt thư viện AI Agent (Dùng PyTorch CPU siêu nhẹ tránh tràn ổ đĩa máy ảo)
echo "4. Cài đặt thư viện Network Agent (CICFlowMeter, Scapy, AI)..."
# Xóa cache tạm để giải phóng dung lượng
pip cache purge || true
# Cài bản PyTorch CPU (~180MB thay vì 4GB CUDA)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install scapy pandas numpy cicflowmeter scikit-learn

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


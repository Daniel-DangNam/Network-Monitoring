#!/bin/bash
set -e
cd "$(dirname "$0")/network_agent"

# Tự động kích hoạt virtual environment nếu có
if [ -d "../venv" ]; then
    source ../venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# Tùy chọn chỉ định card mạng nếu cần (ví dụ ens33 hoặc eth0)
# export NETWORK_INTERFACE="ens33"

echo "=================================================="
echo " [STARTING] AI Network Sniffer Agent on Ubuntu    "
echo "=================================================="
echo "Lưu ý: Sniff raw socket cần quyền root hoặc capability:"
echo "sudo -E $(which python3) live_pipeline.py"
echo "--------------------------------------------------"

if [ "$EUID" -ne 0 ]; then
    echo "-> Đang chạy không có quyền root, tự động gọi sudo..."
    sudo -E "$(which python3)" live_pipeline.py
else
    python3 live_pipeline.py
fi


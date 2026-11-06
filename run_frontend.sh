#!/bin/bash
set -e
cd "$(dirname "$0")/frontend-dashboard"

echo "=================================================="
echo " [STARTING] Vite React Dashboard on Ubuntu        "
echo "=================================================="
if [ ! -d "node_modules" ]; then
    echo "Đang cài đặt thư viện npm..."
    npm install
fi
npm run dev -- --host


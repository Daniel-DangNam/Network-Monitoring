@echo off
title Network AI - Backend API (FastAPI)
cd /d "%~dp0backend_api"
echo ===================================================
echo [1/2] Dang kiem tra va khoi tao tai khoan admin...
echo ===================================================
python scripts/create_admin.py

echo.
echo ===================================================
echo [2/2] Dang khoi chay FastAPI Server tai cong 8000...
echo ===================================================
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
pause


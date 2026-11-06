@echo off
title Network AI - Frontend Dashboard (ReactJS + Vite)
cd /d "%~dp0frontend-dashboard"
echo ===================================================
echo [1/2] Kiem tra dependencies (neu chua co thi install)...
echo ===================================================
if not exist node_modules (
    echo Dang cai dat thu vien Frontend... Vui long doi vai phut...
    call npm install
)

echo.
echo ===================================================
echo [2/2] Dang khoi chay Vite Dev Server...
echo ===================================================
call npm run dev
pause


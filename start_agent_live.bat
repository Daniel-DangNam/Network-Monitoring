@echo off
title Network AI - Network Agent (Live Sniffing & AI)
cd /d "%~dp0network_agent"
echo ===================================================
echo [AI Agent] Dang khoi chay Live Sniffing + ResNet-18...
echo Luu y: Chay script nay voi quyen Administrator neu can bat goi tin!
echo ===================================================
python main.py --mode live
pause

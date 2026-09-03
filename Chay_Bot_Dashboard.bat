@echo off
title SCM Telegram Bot & Dashboard Server
echo ========================================================
echo   DANG KHOI DONG BOT TELEGRAM & WEB DASHBOARD...
echo ========================================================
cd /d "C:\Users\Admin\.gemini\antigravity\scratch\telegram_bot"

echo.
echo [1/2] Khoi dong Cloudflare Tunnel cho phep truy cap tu moi may tinh...
start "" /b cloudflared.exe tunnel --url http://localhost:5000

echo.
echo [2/2] Khoi chay Web Server (FastAPI / Uvicorn)...
echo.
echo --------------------------------------------------------
echo CAC DE NGHl TRUY CAP:
echo - Tren may nay:              http://localhost:5000
echo - Trung mang Wi-Fi / LAN:   http://192.168.1.9:5000
echo - Truy cap TU MOI MAY TINH: Xem duong link https://...trycloudflare.com
echo --------------------------------------------------------
echo.

.\.venv\Scripts\python.exe server.py
pause

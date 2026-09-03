@echo off
title SCM Telegram Bot & Dashboard Server
echo ========================================================
echo   DANG KHOI DONG BOT TELEGRAM & WEB DASHBOARD...
echo ========================================================
cd /d "C:\Users\Admin\.gemini\antigravity\scratch\telegram_bot"

echo.
echo [1/2] Khoi dong Cloudflare Tunnel...
start "" /b cloudflared.exe tunnel --url http://localhost:5000

echo.
echo [2/2] Khoi chay Web Server (FastAPI / Uvicorn)...
echo.
echo --------------------------------------------------------
echo LINK WEBSITE GOC (Truy cap tu moi may tinh va dien thoai):
echo 👉 https://barrel-kodak-jane-residents.trycloudflare.com
echo.
echo Link cuc bo (chi tren may nay):
echo 👉 http://localhost:5000
echo --------------------------------------------------------
echo.

.\.venv\Scripts\python.exe server.py
pause

@echo off
title ระบบเช็คชื่อ Face Recognition - กองแผนงาน

echo.
echo  ╔══════════════════════════════════════════════╗
echo  ║       ระบบเช็คชื่อ Face Recognition          ║
echo  ║              กองแผนงาน                      ║
echo  ╚══════════════════════════════════════════════╝
echo.

echo [INFO] กำลังเริ่มระบบ...

call venv\Scripts\activate.bat

echo [INFO] เริ่ม Backend Server...
cd backend
start "Backend Server" python app.py

echo [INFO] รอ Backend เริ่มทำงาน...
timeout /t 3

echo [INFO] เปิด Frontend...
start "" "..\index.html"

echo.
echo ✅ ระบบพร้อมใช้งาน!
echo.
echo Backend: http://localhost:5000
echo Frontend: เปิดไฟล์ HTML แล้ว
echo.
echo กด Ctrl+C เพื่อหยุดระบบ
echo.
pause

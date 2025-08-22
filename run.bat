@echo off
chcp 65001 >nul
echo ================================================
echo 🚀 Face Attendance System
echo ================================================

cd /d "%~dp0"

echo [1/3] ตรวจสอบ Virtual Environment...
if not exist venv\Scripts\activate.bat (
    echo ❌ ERROR: Virtual Environment ไม่พบ
    echo กรุณารัน install.bat ก่อน
    pause
    exit /b 1
)

echo ✅ พบ Virtual Environment
call venv\Scripts\activate.bat

echo.
echo [2/3] ตรวจสอบ Dependencies...
python -c "import flask, cv2, numpy, pyodbc" 2>nul
if errorlevel 1 (
    echo ❌ ERROR: Dependencies ไม่ครบถ้วน
    echo กรุณารัน install.bat อีกครั้ง
    pause
    exit /b 1
)
echo ✅ Dependencies พร้อม

echo.
echo [3/3] เริ่มต้นเซิร์ฟเวอร์...
if not exist backend\app.py (
    echo ❌ ERROR: ไม่พบไฟล์ backend\app.py
    echo กรุณาตรวจสอบโครงสร้างโปรเจค
    pause
    exit /b 1
)

echo.
echo ================================================
echo 🌐 เซิร์ฟเวอร์กำลังรัน...
echo 📱 เปิด: http://localhost:5000
echo 🛑 หยุด: กด Ctrl+C
echo ================================================
echo.

cd backend
python app.py

echo.
echo ระบบหยุดทำงานแล้ว
pause

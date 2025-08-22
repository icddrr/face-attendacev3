@echo off
chcp 65001 >nul
echo กำลังติดตั้งระบบเช็คชื่อด้วย Face Recognition...
echo.

cd /d "%~dp0"

echo [1/6] ตรวจสอบ Python...
python --version
if errorlevel 1 (
    echo ❌ ERROR: กรุณาติดตั้ง Python ก่อน
    echo    ดาวน์โหลดได้จาก: https://python.org
    pause
    exit /b 1
)

echo.
echo [2/6] ลบ Virtual Environment เก่า (ถ้ามี)...
if exist venv (
    echo กำลังลบ venv เก่า...
    rmdir /s /q venv
)

echo.
echo [3/6] สร้าง Virtual Environment ใหม่...
python -m venv venv
if errorlevel 1 (
    echo ❌ ERROR: ไม่สามารถสร้าง Virtual Environment ได้
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ ERROR: ไม่สามารถเปิดใช้งาน Virtual Environment ได้
    pause
    exit /b 1
)

echo.
echo [4/6] อัปเกรด pip และ setuptools...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo ⚠️ WARNING: อัปเกรด pip ไม่สำเร็จ แต่ดำเนินการต่อ...
)

echo.
echo [5/6] ติดตั้ง Dependencies...
if not exist backend\requirements.txt (
    echo ❌ ERROR: ไม่พบไฟล์ backend\requirements.txt
    echo กำลังสร้างไฟล์ requirements.txt...
    (
        echo flask==2.3.3
        echo flask-cors==4.0.0
        echo opencv-python==4.8.1.78
        echo face-recognition==1.3.0
        echo numpy==1.24.4
        echo pillow==10.0.1
        echo pyodbc==4.0.39
        echo python-dateutil==2.8.2
    ) > backend\requirements.txt
)

cd backend
echo กำลังติดตั้ง packages...
pip install --no-cache-dir -r requirements.txt
if errorlevel 1 (
    echo ⚠️ WARNING: การติดตั้งมีปัญหา กำลังลองวิธีอื่น...
    echo.
    echo กำลังติดตั้งทีละ package...
    pip install --no-cache-dir flask
    pip install --no-cache-dir flask-cors
    pip install --no-cache-dir opencv-python
    pip install --no-cache-dir numpy
    pip install --no-cache-dir pillow
    pip install --no-cache-dir pyodbc
    echo กำลังติดตั้ง face-recognition (อาจใช้เวลานาน)...
    pip install --no-cache-dir face-recognition
)
cd ..

echo.
echo [6/6] ตรวจสอบการติดตั้ง...
python -c "import sys; print(f'Python: {sys.version}')"
python -c "try: import flask; print('✅ Flask: OK')\nexcept: print('❌ Flask: ERROR')"
python -c "try: import cv2; print('✅ OpenCV: OK')\nexcept: print('❌ OpenCV: ERROR')"
python -c "try: import numpy; print('✅ NumPy: OK')\nexcept: print('❌ NumPy: ERROR')"
python -c "try: import PIL; print('✅ Pillow: OK')\nexcept: print('❌ Pillow: ERROR')"
python -c "try: import pyodbc; print('✅ PyODBC: OK')\nexcept: print('❌ PyODBC: ERROR')"
python -c "try: import face_recognition; print('✅ Face Recognition: OK')\nexcept: print('❌ Face Recognition: ERROR (ลองติดตั้งใหม่ด้วย: pip install face-recognition)')"

echo.
echo ================================================
echo 🎉 การติดตั้งเสร็จสิ้น!
echo ================================================
echo.
echo 📋 วิธีการใช้งาน:
echo    1. รันเซิร์ฟเวอร์: run.bat
echo    2. เปิด http://localhost:5000 ในเบราว์เซอร์
echo    3. ทดสอบระบบด้วยการกดปุ่ม "ทดสอบระบบ"
echo.
echo 🔧 ไฟล์ที่สำคัญ:
echo    - backend/app.py (เซิร์ฟเวอร์หลัก)
echo    - frontend/index.html (หน้าเว็บ)
echo    - database/schema.sql (โครงสร้างฐานข้อมูล)
echo.
echo 💡 หากมีปัญหา:
echo    - รีสตาร์ท Command Prompt แบบ Administrator
echo    - ตรวจสอบ Antivirus ไม่บล็อกไฟล์
echo    - ลองรัน: venv\Scripts\activate.bat
echo.
pause

@echo off
echo กำลังติดตั้งระบบเช็คชื่อด้วย Face Recognition...

echo.
echo [1/5] ตรวจสอบ Python...
python --version
if errorlevel 1 (
    echo ERROR: กรุณาติดตั้ง Python ก่อน
    pause
    exit
)

echo.
echo [2/5] สร้าง Virtual Environment...
python -m venv venv
call venv\Scripts\activate.bat

echo.
echo [3/5] อัปเกรด pip...
python -m pip install --upgrade pip

echo.
echo [4/5] ติดตั้ง Dependencies...
cd backend
pip install -r requirements.txt

echo.
echo [5/5] ตรวจสอบการติดตั้ง...
python -c "import flask, cv2, face_recognition, pyodbc; print('✅ ติดตั้งสำเร็จ!')"

echo.
echo 🎉 การติดตั้งเสร็จสิ้น!
echo.
echo วิธีการใช้งาน:
echo 1. เริ่มต้น Backend: python backend/app.py
echo 2. เปิดไฟล์ HTML ในเบราว์เซอร์
echo 3. ทดสอบระบบด้วยการกดปุ่ม "ทดสอบระบบ"
echo.
pause

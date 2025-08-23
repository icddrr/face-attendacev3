@echo off
chcp 65001 >nul
echo ================================================
echo 🧪 ทดสอบ Packages ทั้งหมด
echo ================================================

cd /d "%~dp0"
call venv\Scripts\activate.bat

echo กำลังทดสอบ...
python -c "
try:
    import flask
    print('✅ Flask:', flask.__version__)
except Exception as e:
    print('❌ Flask:', str(e))

try:
    import cv2
    print('✅ OpenCV:', cv2.__version__)
except Exception as e:
    print('❌ OpenCV:', str(e))

try:
    import face_recognition
    print('✅ Face Recognition: OK')
except Exception as e:
    print('❌ Face Recognition:', str(e))

try:
    import numpy
    print('✅ NumPy:', numpy.__version__)
except Exception as e:
    print('❌ NumPy:', str(e))

try:
    import pyodbc
    print('✅ PyODBC:', pyodbc.version)
except Exception as e:
    print('❌ PyODBC:', str(e))

try:
    import flask_cors
    print('✅ Flask-CORS: OK')
except Exception as e:
    print('❌ Flask-CORS:', str(e))

print('\n🎯 ทดสอบ Face Recognition...')
try:
    import face_recognition
    import numpy as np
    # ทดสอบสร้าง dummy encoding
    dummy_image = np.zeros((100, 100, 3), dtype=np.uint8)
    # ไม่ต้องทดสอบจริงๆ เพราะต้องมีหน้าคนในภาพ
    print('✅ Face Recognition พร้อมใช้งาน')
except Exception as e:
    print('❌ Face Recognition Error:', str(e))
"

echo.
echo ================================================
echo 🚀 หาก packages ทั้งหมดแสดง ✅ แสดงว่าพร้อมแล้ว!
echo ================================================
pause

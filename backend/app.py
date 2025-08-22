from flask import Flask, request, jsonify
from flask_cors import CORS
import pyodbc
import json
import numpy as np
from datetime import datetime, date, time
import face_recognition
import cv2
import base64
from io import BytesIO
from PIL import Image
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Database Configuration
DB_CONFIG = {
    'driver': 'ODBC Driver 17 for SQL Server',
    'server': 'localhost',
    'database': 'attendance_system',
    'trusted_connection': 'yes'
}

def get_db_connection():
    """สร้างการเชื่อมต่อฐานข้อมูล"""
    try:
        conn_str = f"DRIVER={{{DB_CONFIG['driver']}}};SERVER={DB_CONFIG['server']};DATABASE={DB_CONFIG['database']};Trusted_Connection={DB_CONFIG['trusted_connection']}"
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def generate_employee_id():
    """สร้างรหัสพนักงานอัตโนมัติ"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM employees")
        count = cursor.fetchone()[0]
        return f"EMP{str(count + 1).zfill(4)}"
    except Exception as e:
        print(f"Error generating employee ID: {e}")
        return None
    finally:
        conn.close()

@app.route('/api/test', methods=['GET'])
def test_connection():
    """ทดสอบการเชื่อมต่อ"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()[0]
            conn.close()
            return jsonify({
                'success': True,
                'message': 'Database connected successfully',
                'data': {'database': 'attendance_system', 'version': version}
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Database error: {str(e)}'
            })
    else:
        return jsonify({
            'success': False,
            'message': 'Unable to connect to database'
        })

@app.route('/api/departments', methods=['GET'])
def get_departments():
    """ดึงข้อมูลแผนกทั้งหมด"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'})
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, dept_name, dept_code FROM departments ORDER BY id")
        departments = []
        for row in cursor.fetchall():
            departments.append({
                'id': row[0],
                'dept_name': row[1],
                'dept_code': row[2]
            })
        
        return jsonify({
            'success': True,
            'data': departments
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })
    finally:
        conn.close()

@app.route('/api/register_employee', methods=['POST'])
def register_employee():
    """ลงทะเบียนพนักงานใหม่"""
    data = request.get_json()
    
    required_fields = ['name', 'department_id', 'position']
    if not all(field in data for field in required_fields):
        return jsonify({
            'success': False,
            'message': 'กรุณากรอกข้อมูลที่จำเป็นให้ครบถ้วน'
        })
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'})
    
    try:
        employee_id = generate_employee_id()
        if not employee_id:
            return jsonify({
                'success': False,
                'message': 'ไม่สามารถสร้างรหัสพนักงานได้'
            })
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO employees (employee_id, name, department_id, position, email, phone)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            employee_id,
            data['name'],
            data['department_id'],
            data['position'],
            data.get('email'),
            data.get('phone')
        ))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'ลงทะเบียนพนักงานสำเร็จ',
            'data': {'employee_id': employee_id}
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'เกิดข้อผิดพลาด: {str(e)}'
        })
    finally:
        conn.close()

@app.route('/api/register_face', methods=['POST'])
def register_face():
    """บันทึกใบหน้าของพนักงาน"""
    data = request.get_json()
    
    if not data.get('employee_id') or not data.get('face_descriptor'):
        return jsonify({
            'success': False,
            'message': 'ข้อมูลไม่ครบถ้วน'
        })
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'})
    
    try:
        cursor = conn.cursor()
        
        # ตรวจสอบว่าพนักงานมีอยู่หรือไม่
        cursor.execute("SELECT employee_id FROM employees WHERE employee_id = ?", (data['employee_id'],))
        if not cursor.fetchone():
            return jsonify({
                'success': False,
                'message': 'ไม่พบข้อมูลพนักงาน'
            })
        
        # บันทึก face descriptor
        face_descriptor_json = json.dumps(data['face_descriptor'])
        cursor.execute("""
            UPDATE employees 
            SET face_descriptor = ?, updated_at = GETDATE()
            WHERE employee_id = ?
        """, (face_descriptor_json, data['employee_id']))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'บันทึกใบหน้าสำเร็จ'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'เกิดข้อผิดพลาด: {str(e)}'
        })
    finally:
        conn.close()

@app.route('/api/employees', methods=['GET'])
def get_employees():
    """ดึงข้อมูลพนักงานทั้งหมด"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'})
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.employee_id, e.name, e.position, e.email, e.phone, 
                   d.dept_name, d.dept_code, e.face_descriptor
            FROM employees e
            LEFT JOIN departments d ON e.department_id = d.id
            ORDER BY e.employee_id
        """)
        
        employees = []
        for row in cursor.fetchall():
            employees.append({
                'employee_id': row[0],
                'name': row[1],
                'position': row[2],
                'email': row[3],
                'phone': row[4],
                'dept_name': row[5],
                'dept_code': row[6],
                'face_descriptor': 'registered' if row[7] else None
            })
        
        return jsonify({
            'success': True,
            'data': employees
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })
    finally:
        conn.close()

def find_face_match(face_descriptor):
    """ค้นหาใบหน้าที่ตรงกัน"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT employee_id, name, face_descriptor
            FROM employees
            WHERE face_descriptor IS NOT NULL
        """)
        
        input_encoding = np.array(face_descriptor)
        best_match = None
        best_distance = 0.6  # threshold สำหรับการจดจำใบหน้า
        
        for row in cursor.fetchall():
            stored_encoding = np.array(json.loads(row[2]))
            distance = np.linalg.norm(input_encoding - stored_encoding)
            
            if distance < best_distance:
                best_distance = distance
                best_match = {
                    'employee_id': row[0],
                    'name': row[1],
                    'distance': distance
                }
        
        return best_match
        
    except Exception as e:
        print(f"Face matching error: {e}")
        return None
    finally:
        conn.close()

@app.route('/api/check_attendance', methods=['POST'])
def check_attendance():
    """เช็คชื่อเข้า-ออกทำงาน"""
    data = request.get_json()
    
    if not data.get('face_descriptor'):
        return jsonify({
            'success': False,
            'message': 'ไม่พบข้อมูลใบหน้า'
        })
    
    # ค้นหาใบหน้าที่ตรงกัน
    match = find_face_match(data['face_descriptor'])
    if not match:
        return jsonify({
            'success': False,
            'message': 'ไม่พบใบหน้าในระบบ กรุณาลงทะเบียนก่อน'
        })
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'})
    
    try:
        employee_id = match['employee_id']
        today = date.today()
        now = datetime.now().time()
        
        cursor = conn.cursor()
        
        # ดึงข้อมูลพนักงาน
        cursor.execute("""
            SELECT e.name, e.position, d.dept_name
            FROM employees e
            LEFT JOIN departments d ON e.department_id = d.id
            WHERE e.employee_id = ?
        """, (employee_id,))
        
        employee_info = cursor.fetchone()
        if not employee_info:
            return jsonify({
                'success': False,
                'message': 'ไม่พบข้อมูลพนักงาน'
            })
        
        # ตรวจสอบการเช็คชื่อวันนี้
        cursor.execute("""
            SELECT check_in_time, check_out_time
            FROM attendance
            WHERE employee_id = ? AND date = ?
        """, (employee_id, today))
        
        attendance_record = cursor.fetchone()
        
        if not attendance_record:
            # เช็คอิน (ครั้งแรก)
            cursor.execute("""
                INSERT INTO attendance (employee_id, date, check_in_time, status)
                VALUES (?, ?, ?, 'checked_in')
            """, (employee_id, today, now))
            action = 'check_in'
            
        elif not attendance_record[1]:  # ยังไม่เช็คเอาท์
            # เช็คเอาท์
            check_in_time = attendance_record[0]
            working_hours = calculate_working_hours(check_in_time, now)
            
            cursor.execute("""
                UPDATE attendance
                SET check_out_time = ?, status = 'checked_out', working_hours = ?
                WHERE employee_id = ? AND date = ?
            """, (now, working_hours, employee_id, today))
            action = 'check_out'
            
        else:
            return jsonify({
                'success': False,
                'message': 'วันนี้คุณเช็คชื่อครบแล้ว'
            })
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': f'เช็ค{"เข้า" if action == "check_in" else "ออก"}ทำงานสำเร็จ',
            'data': {
                'employee': {
                    'employee_id': employee_id,
                    'name': employee_info[0],
                    'position': employee_info[1],
                    'dept_name': employee_info[2]
                },
                'action': action,
                'time': now.strftime('%H:%M:%S')
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'เกิดข้อผิดพลาด: {str(e)}'
        })
    finally:
        conn.close()

def calculate_working_hours(check_in, check_out):
    """คำนวณชั่วโมงทำงาน"""
    if isinstance(check_in, str):
        check_in = datetime.strptime(check_in, '%H:%M:%S').time()
    if isinstance(check_out, str):
        check_out = datetime.strptime(check_out, '%H:%M:%S').time()
    
    # แปลงเป็น datetime เพื่อคำนวณ
    today = date.today()
    dt_in = datetime.combine(today, check_in)
    dt_out = datetime.combine(today, check_out)
    
    # หากเวลาออกน้อยกว่าเวลาเข้า แสดงว่าข้ามวัน
    if dt_out < dt_in:
        dt_out += timedelta(days=1)
    
    diff = dt_out - dt_in
    return round(diff.total_seconds() / 3600, 2)

@app.route('/api/attendance', methods=['GET'])
def get_attendance():
    """ดึงข้อมูลการเช็คชื่อ"""
    date_param = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'})
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.date, e.name, d.dept_name, a.check_in_time, 
                   a.check_out_time, a.status, a.working_hours
            FROM attendance a
            JOIN employees e ON a.employee_id = e.employee_id
            LEFT JOIN departments d ON e.department_id = d.id
            WHERE a.date = ?
            ORDER BY a.check_in_time
        """, (date_param,))
        
        attendance_records = []
        for row in cursor.fetchall():
            attendance_records.append({
                'date': row[0].strftime('%Y-%m-%d') if row[0] else None,
                'name': row[1],
                'dept_name': row[2],
                'check_in_time': row[3].strftime('%H:%M:%S') if row[3] else None,
                'check_out_time': row[4].strftime('%H:%M:%S') if row[4] else None,
                'status': row[5],
                'working_hours': float(row[6]) if row[6] else 0
            })
        
        return jsonify({
            'success': True,
            'data': attendance_records
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

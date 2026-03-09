from flask import Blueprint, render_template

from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db import get_db_connection
from werkzeug.security import generate_password_hash
import uuid

users_bp = Blueprint('users', __name__)

@users_bp.route('/')
def list_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users ORDER BY id DESC').fetchall()
    # Convert Row objects to dictionaries
    users_list = [dict(row) for row in users]
    conn.close()
    return render_template('admin/users.html', users=users_list)

@users_bp.route('/add', methods=['POST'])
def add_user():
    name = request.form['name']
    department = request.form['department']
    roll_number = request.form['roll_number']
    phone = request.form.get('phone', '')
    email = request.form.get('email', '')
    
    # Generate automatic values
    library_id = "LIB-" + str(uuid.uuid4().int)[:8]
    barcode = request.form.get('barcode') or str(uuid.uuid4().int)[:12]
    qr_code = library_id # For now, simple textual representation, QR Image generation handled later
    password_hash = generate_password_hash(roll_number) # default password is roll number
    
    conn = get_db_connection()
    try:
        conn.execute('''
            INSERT INTO users (library_id, name, department, roll_number, phone, email, qr_code, barcode, password_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (library_id, name, department, roll_number, phone, email, qr_code, barcode, password_hash))
        conn.commit()
        flash('Student added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding student: {str(e)}', 'error')
    finally:
        conn.close()
        
    return redirect(url_for('users.list_users'))

@users_bp.route('/edit/<int:user_id>', methods=['POST'])
def edit_user(user_id):
    name = request.form['name']
    department = request.form['department']
    roll_number = request.form['roll_number']
    phone = request.form.get('phone', '')
    email = request.form.get('email', '')
    
    conn = get_db_connection()
    try:
        conn.execute('''
            UPDATE users SET name=?, department=?, roll_number=?, phone=?, email=?
            WHERE id=?
        ''', (name, department, roll_number, phone, email, user_id))
        conn.commit()
        flash('Student updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating student: {str(e)}', 'error')
    finally:
        conn.close()
        
    return redirect(url_for('users.list_users'))

@users_bp.route('/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    conn = get_db_connection()
    try:
        # Prevent deletion if user has issued books
        issued_count = conn.execute('SELECT COUNT(*) FROM issued_books WHERE user_id = ? AND status="issued"', (user_id,)).fetchone()[0]
        if issued_count > 0:
            flash('Cannot delete student: They have currently issued books.', 'error')
        else:
            conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            flash('Student deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting student: {str(e)}', 'error')
    finally:
        conn.close()
        
    return redirect(url_for('users.list_users'))


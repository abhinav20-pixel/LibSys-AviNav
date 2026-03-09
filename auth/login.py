from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from database.db import get_db_connection

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        admin = conn.execute('SELECT * FROM admins WHERE username = ?', (username,)).fetchone()
        
        if admin and check_password_hash(admin['password_hash'], password):
            session['user_id'] = admin['id']
            session['username'] = admin['username']
            session['role'] = 'admin'
            conn.close()
            return redirect(url_for('dashboard.admin_home'))
            
        student = conn.execute('SELECT * FROM users WHERE roll_number = ? OR email = ? OR library_id = ?', 
                               (username, username, username)).fetchone()
        
        if student and check_password_hash(student['password_hash'], password):
            session['user_id'] = student['id']
            session['username'] = student['name']
            session['role'] = 'student'
            conn.close()
            return redirect(url_for('student_dashboard'))
            
        conn.close()
        flash('Invalid credentials. Please try again.', 'error')
        
    return render_template('public/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

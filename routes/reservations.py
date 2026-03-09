from flask import Blueprint, render_template

from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db import get_db_connection

reservations_bp = Blueprint('reservations', __name__)

@reservations_bp.route('/')
def list_reservations():
    conn = get_db_connection()
    reservations = conn.execute('''
        SELECT r.*, u.name as user_name, u.library_id, b.title as book_title, b.available_copies
        FROM reservations r
        JOIN users u ON r.user_id = u.id
        JOIN books b ON r.book_id = b.id
        ORDER BY 
            CASE status 
                WHEN 'pending' THEN 1 
                WHEN 'approved' THEN 2 
                ELSE 3 
            END, r.id DESC
    ''').fetchall()
    conn.close()
    return render_template('admin/reservations.html', reservations=reservations)

@reservations_bp.route('/update/<int:res_id>', methods=['POST'])
def update_reservation(res_id):
    action = request.form.get('action')
    conn = get_db_connection()
    try:
        if action == 'approve':
            # Check availability
            res = conn.execute('SELECT book_id FROM reservations WHERE id=?', (res_id,)).fetchone()
            book = conn.execute('SELECT available_copies FROM books WHERE id=?', (res['book_id'],)).fetchone()
            
            if book['available_copies'] > 0:
                conn.execute('UPDATE reservations SET status="approved" WHERE id=?', (res_id,))
                conn.execute('UPDATE books SET available_copies = available_copies - 1 WHERE id=?', (res['book_id'],))
                flash('Reservation approved. The book is held for the student.', 'success')
            else:
                flash('Cannot approve: No copies currently available.', 'error')
                
        elif action == 'reject':
            # If rejecting an approved res, we give the book copy back
            status = conn.execute('SELECT status, book_id FROM reservations WHERE id=?', (res_id,)).fetchone()
            if status['status'] == 'approved':
                conn.execute('UPDATE books SET available_copies = available_copies + 1 WHERE id=?', (status['book_id'],))
                
            conn.execute('UPDATE reservations SET status="rejected" WHERE id=?', (res_id,))
            flash('Reservation rejected.', 'success')
            
        elif action == 'complete':
            # Finished (book was actually issued or returned later, mostly unhooks reservation)
            conn.execute('UPDATE reservations SET status="completed" WHERE id=?', (res_id,))
            flash('Reservation marked as completed.', 'success')
            
        conn.commit()
    except Exception as e:
        conn.rollback()
        flash(f'Error updating reservation: {str(e)}', 'error')
    finally:
        conn.close()
        
    return redirect(url_for('reservations.list_reservations'))


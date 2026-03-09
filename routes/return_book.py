from flask import Blueprint, render_template

from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db import get_db_connection
from datetime import datetime

return_bp = Blueprint('return', __name__)

FINE_PER_DAY = 5.0

@return_bp.route('/', methods=['GET', 'POST'])
def return_book():
    conn = get_db_connection()
    issued_records = []
    student = None
    
    # Handle Scan Search
    if request.method == 'POST' and 'search' in request.form:
        student_qr = request.form.get('student_qr', '').strip()
        book_barcode = request.form.get('book_barcode', '').strip()
        
        query = '''
            SELECT ib.*, u.name as user_name, u.library_id, u.qr_code, 
                   b.title as book_title, b.barcode, b.author
            FROM issued_books ib
            JOIN users u ON ib.user_id = u.id
            JOIN books b ON ib.book_id = b.id
            WHERE ib.status = "issued"
        '''
        params = []
        
        if student_qr:
            query += ' AND (u.qr_code = ? OR u.library_id = ?)'
            params.extend([student_qr, student_qr])
            student = conn.execute('SELECT * FROM users WHERE qr_code=? OR library_id=?', (student_qr, student_qr)).fetchone()
            
        if book_barcode:
            query += ' AND b.barcode = ?'
            params.append(book_barcode)
            
        issued_records = conn.execute(query, params).fetchall()
        
        if not issued_records:
            flash("No active issued books found for the provided scan data.", "error")
            
        # Calculate fines dynamically for display
        calculated_records = []
        for record in issued_records:
            rec = dict(record)
            deadline = datetime.strptime(rec['return_deadline'], '%Y-%m-%d %H:%M:%S')
            now = datetime.now()
            
            late_days = 0
            fine = 0.0
            if now > deadline:
                late_days = (now - deadline).days
                if late_days == 0 and (now - deadline).seconds > 0:
                    late_days = 1 # partial day late
                fine = late_days * FINE_PER_DAY
                
            rec['late_days'] = late_days
            rec['fine_amount'] = fine
            calculated_records.append(rec)
            
        issued_records = calculated_records

    # Handle Return Action
    if request.method == 'POST' and 'return_action' in request.form:
        issue_id = request.form.get('issue_id')
        user_id = request.form.get('user_id')
        book_id = request.form.get('book_id')
        late_days = int(request.form.get('late_days', 0))
        fine_amount = float(request.form.get('fine_amount', 0.0))
        payment_received = request.form.get('payment_received') == 'yes'
        
        try:
            # 1. Update book availability
            conn.execute('UPDATE books SET available_copies = available_copies + 1 WHERE id = ?', (book_id,))
            
            # 2. Update issue status
            conn.execute('UPDATE issued_books SET status = "returned" WHERE id = ?', (issue_id,))
            
            # 3. Create fine record if applicable
            if fine_amount > 0:
                fine_status = 'paid' if payment_received else 'unpaid'
                conn.execute('''
                    INSERT INTO fines (user_id, book_id, late_days, fine_amount, status)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, book_id, late_days, fine_amount, fine_status))
                
            # 4. Activity log
            student_name = conn.execute('SELECT name FROM users WHERE id=?', (user_id,)).fetchone()[0]
            book_title = conn.execute('SELECT title FROM books WHERE id=?', (book_id,)).fetchone()[0]
            msg = f'Returned "{book_title}" from {student_name}.'
            if fine_amount > 0:
                msg += f' Fine: ₹{fine_amount} ({paid_str})'
                paid_str = "Paid" if payment_received else "Unpaid"
            
            conn.execute('INSERT INTO activity_logs (action, details) VALUES (?, ?)', ('Book Returned', msg))
            
            conn.commit()
            flash(f'Book successfully returned!', 'success')
            return redirect(url_for('return.return_book'))
            
        except Exception as e:
            conn.rollback()
            flash(f"Error returning book: {str(e)}", "error")

    # Get recent returns for the table (just for context)
    recent_returns = conn.execute('''
        SELECT ib.*, u.name as user_name, u.library_id, b.title as book_title
        FROM issued_books ib
        JOIN users u ON ib.user_id = u.id
        JOIN books b ON ib.book_id = b.id
        WHERE ib.status = "returned"
        ORDER BY ib.id DESC LIMIT 10
    ''').fetchall()

    conn.close()
    return render_template('admin/return.html', issued_records=issued_records, student=student, recent_returns=recent_returns)


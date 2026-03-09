from flask import Blueprint, render_template

from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db import get_db_connection
from datetime import datetime, timedelta

issue_bp = Blueprint('issue', __name__)

@issue_bp.route('/', methods=['GET', 'POST'])
def issue_book():
    conn = get_db_connection()
    student = None
    book = None
    
    # Handle scan/search
    if request.method == 'POST' and 'search' in request.form:
        student_qr = request.form.get('student_qr', '').strip()
        book_barcode = request.form.get('book_barcode', '').strip()
        
        if student_qr:
            student = conn.execute('SELECT * FROM users WHERE qr_code = ? OR library_id = ? OR roll_number = ?', 
                                   (student_qr, student_qr, student_qr)).fetchone()
            if not student:
                flash("Student not found.", "error")
                
        if book_barcode:
            book = conn.execute('SELECT * FROM books WHERE barcode = ? OR isbn = ?', 
                                (book_barcode, book_barcode)).fetchone()
            if not book:
                flash("Book not found.", "error")
            elif book['available_copies'] <= 0:
                flash("Book is currently out of stock.", "error")
                book = None
                
    # Handle actual issue action
    if request.method == 'POST' and 'issue' in request.form:
        user_id = request.form.get('user_id')
        book_id = request.form.get('book_id')
        days = int(request.form.get('days', 14))
        
        if user_id and book_id:
            try:
                # Check for existing issue of the same book
                existing = conn.execute('SELECT id FROM issued_books WHERE user_id=? AND book_id=? AND status="issued"', (user_id, book_id)).fetchone()
                if existing:
                    flash("Student already has this book issued.", "error")
                else:
                    issue_date = datetime.now()
                    return_deadline = issue_date + timedelta(days=days)
                    
                    # Update stock
                    conn.execute('UPDATE books SET available_copies = available_copies - 1 WHERE id = ?', (book_id,))
                    
                    # Record issue
                    conn.execute('''
                        INSERT INTO issued_books (user_id, book_id, issue_date, return_deadline, status)
                        VALUES (?, ?, ?, ?, 'issued')
                    ''', (user_id, book_id, issue_date.strftime('%Y-%m-%d %H:%M:%S'), return_deadline.strftime('%Y-%m-%d %H:%M:%S')))
                    
                    # Log activity
                    student_name = conn.execute('SELECT name FROM users WHERE id=?', (user_id,)).fetchone()[0]
                    book_title = conn.execute('SELECT title FROM books WHERE id=?', (book_id,)).fetchone()[0]
                    conn.execute('INSERT INTO activity_logs (action, details) VALUES (?, ?)', 
                                ('Book Issued', f'Issued "{book_title}" to {student_name}'))
                    
                    conn.commit()
                    flash(f'Book issued successfully! Due back on {return_deadline.strftime("%B %d, %Y")}', 'success')
                    return redirect(url_for('issue.issue_book'))
                    
            except Exception as e:
                flash(f"Error issuing book: {str(e)}", "error")
                conn.rollback()

    # Get recent issues for the table
    recent_issues = conn.execute('''
        SELECT ib.*, u.name as user_name, u.library_id, b.title as book_title
        FROM issued_books ib
        JOIN users u ON ib.user_id = u.id
        JOIN books b ON ib.book_id = b.id
        ORDER BY ib.id DESC LIMIT 10
    ''').fetchall()
    
    conn.close()
    return render_template('admin/issue.html', student=student, book=book, recent_issues=recent_issues)


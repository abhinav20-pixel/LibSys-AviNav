from flask import Blueprint, render_template

from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db import get_db_connection
import uuid

books_bp = Blueprint('books', __name__)

@books_bp.route('/')
def list_books():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books ORDER BY id DESC').fetchall()
    # Convert Row objects to dictionaries 
    books_list = [dict(row) for row in books]
    conn.close()
    return render_template('admin/books.html', books=books_list)

@books_bp.route('/add', methods=['POST'])
def add_book():
    title = request.form['title']
    author = request.form['author']
    category = request.form['category']
    isbn = request.form['isbn']
    barcode = request.form.get('barcode') or str(uuid.uuid4().int)[:12]  # Default barcode if empty
    quantity = int(request.form['quantity'])
    rack_number = request.form['rack_number']
    
    conn = get_db_connection()
    try:
        conn.execute('''
            INSERT INTO books (title, author, category, isbn, barcode, quantity, available_copies, rack_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, author, category, isbn, barcode, quantity, quantity, rack_number))
        conn.commit()
        flash('Book added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding book: {str(e)}', 'error')
    finally:
        conn.close()
        
    return redirect(url_for('books.list_books'))

@books_bp.route('/edit/<int:book_id>', methods=['POST'])
def edit_book(book_id):
    title = request.form['title']
    author = request.form['author']
    category = request.form['category']
    isbn = request.form['isbn']
    barcode = request.form['barcode']
    quantity = int(request.form['quantity'])
    rack_number = request.form['rack_number']
    
    conn = get_db_connection()
    try:
        # Calculate available copies based on new total quantity minus issued books
        issued_count = conn.execute('SELECT COUNT(*) FROM issued_books WHERE book_id = ? AND status="issued"', (book_id,)).fetchone()[0]
        available_copies = max(0, quantity - issued_count)
        
        conn.execute('''
            UPDATE books SET title=?, author=?, category=?, isbn=?, barcode=?, quantity=?, available_copies=?, rack_number=?
            WHERE id=?
        ''', (title, author, category, isbn, barcode, quantity, available_copies, rack_number, book_id))
        conn.commit()
        flash('Book updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating book: {str(e)}', 'error')
    finally:
        conn.close()
        
    return redirect(url_for('books.list_books'))

@books_bp.route('/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    conn = get_db_connection()
    try:
        # Prevent deletion if books are issued
        issued_count = conn.execute('SELECT COUNT(*) FROM issued_books WHERE book_id = ? AND status="issued"', (book_id,)).fetchone()[0]
        if issued_count > 0:
            flash('Cannot delete book: Copies are currently issued.', 'error')
        else:
            conn.execute('DELETE FROM books WHERE id = ?', (book_id,))
            conn.commit()
            flash('Book deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting book: {str(e)}', 'error')
    finally:
        conn.close()
        
    return redirect(url_for('books.list_books'))


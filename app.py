from flask import Flask, render_template, session, redirect, url_for, flash, request
from config import Config
from database.db import get_db_connection

app = Flask(__name__, template_folder='templates', static_folder='assets')
app.config.from_object(Config)

# Register Blueprints
from auth.login import auth_bp
from routes.dashboard import dashboard_bp
from routes.books import books_bp
from routes.users import users_bp
from routes.issue_book import issue_bp
from routes.return_book import return_bp
from routes.reservations import reservations_bp
from routes.reports import reports_bp
from cards.generate_card import cards_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(dashboard_bp, url_prefix='/admin')
app.register_blueprint(books_bp, url_prefix='/admin/books')
app.register_blueprint(users_bp, url_prefix='/admin/users')
app.register_blueprint(issue_bp, url_prefix='/admin/issue')
app.register_blueprint(return_bp, url_prefix='/admin/return')
app.register_blueprint(reservations_bp, url_prefix='/admin/reservations')
app.register_blueprint(reports_bp, url_prefix='/admin/reports')
app.register_blueprint(cards_bp, url_prefix='/admin/cards')

@app.route('/')
def index():
    # Public portal home page
    books = []
    try:
        conn = get_db_connection()
        books = conn.execute('SELECT * FROM books ORDER BY id DESC LIMIT 6').fetchall()
        conn.close()
    except:
        pass
    return render_template('public/index.html', books=books)

@app.route('/browse')
def browse():
    # Public portal browse
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books').fetchall()
    conn.close()
    return render_template('public/browse.html', books=books)

@app.route('/student')
def student_dashboard():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('auth.login'))
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    issued_books = conn.execute('''
        SELECT ib.*, b.title, b.author, b.cover_image
        FROM issued_books ib 
        JOIN books b ON ib.book_id = b.id 
        WHERE ib.user_id = ? AND ib.status = "issued"
    ''', (session['user_id'],)).fetchall()
    
    reservations = conn.execute('''
        SELECT r.*, b.title, b.author
        FROM reservations r 
        JOIN books b ON r.book_id = b.id 
        WHERE r.user_id = ?
        ORDER BY r.id DESC
    ''', (session['user_id'],)).fetchall()
    
    # AI Recommendation Logic: Books popular in student's department, or fallback to random available
    recommendations = conn.execute('''
        SELECT DISTINCT b.*
        FROM books b
        WHERE b.id NOT IN (SELECT book_id FROM issued_books WHERE user_id = ?)
        AND b.id NOT IN (SELECT book_id FROM reservations WHERE user_id = ? AND status != 'completed' AND status != 'rejected')
        AND b.available_copies > 0
        ORDER BY RANDOM()
        LIMIT 4
    ''', (session['user_id'], session['user_id'])).fetchall()
    
    conn.close()
    return render_template('student/dashboard.html', user=user, issued_books=issued_books, reservations=reservations, recommendations=recommendations)

@app.route('/reserve/<int:book_id>', methods=['POST'])
def reserve_book(book_id):
    if 'user_id' not in session or session.get('role') != 'student':
        flash("You must be logged in as a student to reserve books.", "error")
        return redirect(url_for('auth.login'))
        
    conn = get_db_connection()
    try:
        # Check if book exists and is available
        book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
        if not book:
            flash("Book not found.", "error")
            return redirect(request.referrer or url_for('browse'))
            
        if book['available_copies'] <= 0:
            flash("Book is currently out of stock.", "error")
            return redirect(request.referrer or url_for('browse'))
            
        # Check if already reserved
        existing = conn.execute('SELECT id FROM reservations WHERE user_id=? AND book_id=? AND status IN ("pending", "approved")', 
                                (session['user_id'], book_id)).fetchone()
        if existing:
            flash("You already have an active reservation for this book.", "error")
        else:
            import datetime
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            conn.execute('INSERT INTO reservations (user_id, book_id, reservation_date, status) VALUES (?, ?, ?, "pending")', 
                         (session['user_id'], book_id, now))
            conn.commit()
            flash("Book reserved successfully. Awaiting admin approval.", "success")
            
    except Exception as e:
        flash(f"Error reserving book: {str(e)}", "error")
    finally:
        conn.close()
        
    return redirect(request.referrer or url_for('student_dashboard'))

@app.context_processor
def inject_user():
    return dict(role=session.get('role'), user_id=session.get('user_id'), username=session.get('username'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)

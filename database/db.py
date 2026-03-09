import sqlite3
import os

def get_db_connection():
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'library.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()

    # Create admins table
    c.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')

    # Create users (students) table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            library_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            roll_number TEXT UNIQUE NOT NULL,
            phone TEXT,
            email TEXT UNIQUE,
            photo TEXT,
            qr_code TEXT,
            barcode TEXT,
            password_hash TEXT NOT NULL
        )
    ''')

    # Create books table
    c.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            category TEXT,
            isbn TEXT,
            barcode TEXT UNIQUE,
            quantity INTEGER NOT NULL DEFAULT 1,
            available_copies INTEGER NOT NULL DEFAULT 1,
            rack_number TEXT,
            cover_image TEXT
        )
    ''')

    # Create issued_books table
    c.execute('''
        CREATE TABLE IF NOT EXISTS issued_books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            issue_date DATETIME NOT NULL,
            return_deadline DATETIME NOT NULL,
            status TEXT DEFAULT 'issued',
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(book_id) REFERENCES books(id)
        )
    ''')

    # Create reservations table
    c.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            reservation_date DATETIME NOT NULL,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(book_id) REFERENCES books(id)
        )
    ''')
    
    # Create fines table
    c.execute('''
        CREATE TABLE IF NOT EXISTS fines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            late_days INTEGER NOT NULL,
            fine_amount REAL NOT NULL,
            status TEXT DEFAULT 'unpaid',
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(book_id) REFERENCES books(id)
        )
    ''')

    # Create activity_logs table
    c.execute('''
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            details TEXT
        )
    ''')

    # Insert default admin if not exists
    from werkzeug.security import generate_password_hash
    c.execute('SELECT id FROM admins WHERE username = ?', ('admin',))
    if not c.fetchone():
        c.execute('INSERT INTO admins (username, password_hash) VALUES (?, ?)', 
                  ('admin', generate_password_hash('admin123')))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    # Initialize when run directly
    init_db()
    print("Database initialized successfully.")

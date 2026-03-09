from flask import Blueprint, render_template

from database.db import get_db_connection

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def admin_home():
    conn = get_db_connection()
    stats = {}
    stats['total_books'] = conn.execute('SELECT SUM(quantity) FROM books').fetchone()[0] or 0
    stats['total_users'] = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0] or 0
    stats['books_issued'] = conn.execute('SELECT COUNT(*) FROM issued_books WHERE status="issued"').fetchone()[0] or 0
    stats['overdue_books'] = conn.execute('SELECT COUNT(*) FROM issued_books WHERE status="issued" AND return_deadline < CURRENT_TIMESTAMP').fetchone()[0] or 0
    stats['fine_collected'] = conn.execute('SELECT SUM(fine_amount) FROM fines WHERE status="paid"').fetchone()[0] or 0
    stats['online_reservations'] = conn.execute('SELECT COUNT(*) FROM reservations WHERE status="pending"').fetchone()[0] or 0
    conn.close()
    return render_template('admin/dashboard.html', stats=stats)


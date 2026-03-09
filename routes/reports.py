from flask import Blueprint, render_template

from flask import Blueprint, render_template, request, make_response
from database.db import get_db_connection
import csv
import io

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/')
def view_reports():
    conn = get_db_connection()
    
    # Get recent activities
    activities = conn.execute('SELECT * FROM activity_logs ORDER BY timestamp DESC LIMIT 20').fetchall()
    
    # Get fines data
    fines = conn.execute('''
        SELECT f.*, u.name as user_name, u.library_id, b.title as book_title
        FROM fines f
        JOIN users u ON f.user_id = u.id
        JOIN books b ON f.book_id = b.id
        ORDER BY f.id DESC
    ''').fetchall()
    
    conn.close()
    return render_template('admin/reports.html', activities=activities, fines=fines)

@reports_bp.route('/export/fines')
def export_fines_csv():
    conn = get_db_connection()
    fines = conn.execute('''
        SELECT f.id, u.name, u.library_id, b.title, f.late_days, f.fine_amount, f.status
        FROM fines f
        JOIN users u ON f.user_id = u.id
        JOIN books b ON f.book_id = b.id
        ORDER BY f.id DESC
    ''').fetchall()
    conn.close()
    
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Fine ID', 'Student Name', 'Library ID', 'Book Title', 'Late Days', 'Fine Amount', 'Status'])
    
    for row in fines:
        cw.writerow([row['id'], row['name'], row['library_id'], row['title'], row['late_days'], f"₹{row['fine_amount']}", row['status']])
        
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=fines_report.csv"
    output.headers["Content-type"] = "text/csv"
    return output


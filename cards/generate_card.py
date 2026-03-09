from flask import Blueprint, render_template

from flask import Blueprint, render_template, request, make_response, send_file
from database.db import get_db_connection
import qrcode
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
import base64

cards_bp = Blueprint('cards', __name__)

@cards_bp.route('/')
def generate_card():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('admin/cards.html', users=users)

@cards_bp.route('/qr/<string:data>')
def generate_qr(data):
    img = qrcode.make(data)
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

@cards_bp.route('/barcode/<string:data>')
def generate_barcode(data):
    # Using Code128 standard
    code128 = barcode.get_barcode_class('code128')
    # Use write instead of ImageWriter if rendering to BytesIO
    rv = BytesIO()
    # ImageWriter doesn't take parameters well for base64 inside templates, so we return image
    code128(data, writer=ImageWriter()).write(rv)
    rv.seek(0)
    return send_file(rv, mimetype='image/png')


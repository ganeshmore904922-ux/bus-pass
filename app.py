from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
import qrcode
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Folders
UPLOAD_FOLDER = 'static/uploads'
QR_FOLDER = 'static/qr'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['QR_FOLDER'] = QR_FOLDER

# Create folders automatically
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)


# Database Connection
def get_db_connection():
    conn = sqlite3.connect('buspass.db')
    conn.row_factory = sqlite3.Row
    return conn


# Create Table
def create_table():
    conn = get_db_connection()

    conn.execute('''
        CREATE TABLE IF NOT EXISTS passes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT,
            gender TEXT,
            dob TEXT,
            mobile TEXT,
            email TEXT,
            address TEXT,
            source TEXT,
            destination TEXT,
            pass_type TEXT,
            photo TEXT
        )
    ''')

    conn.commit()
    conn.close()


create_table()


# Dashboard
@app.route('/')
def dashboard():

    conn = get_db_connection()

    total_pass = conn.execute(
        'SELECT COUNT(*) FROM passes'
    ).fetchone()[0]

    conn.close()

    return render_template(
        'dashboard.html',
        total_pass=total_pass
    )


# Add Pass
@app.route('/add-pass', methods=['GET', 'POST'])
def add_pass():

    if request.method == 'POST':

        fullname = request.form['fullname']
        gender = request.form['gender']
        dob = request.form['dob']
        mobile = request.form['mobile']
        email = request.form['email']
        address = request.form['address']
        source = request.form['source']
        destination = request.form['destination']
        pass_type = request.form['pass_type']

        photo = request.files['photo']
        filename = ""

        if photo and photo.filename != "":
            filename = secure_filename(photo.filename)

            photo.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    filename
                )
            )

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO passes
            (
                fullname,
                gender,
                dob,
                mobile,
                email,
                address,
                source,
                destination,
                pass_type,
                photo
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            fullname,
            gender,
            dob,
            mobile,
            email,
            address,
            source,
            destination,
            pass_type,
            filename
        ))

        conn.commit()

        # QR Code Generate
        pass_id = cursor.lastrowid

        # Your Laptop IP Address
       img = qrcode.make(f"https://bus-pass-awm8.onrender.com/pass/{pass_id}")

        qr = qrcode.make(qr_link)

        qr.save(
            os.path.join(
                app.config['QR_FOLDER'],
                f'{pass_id}.png'
            )
        )

        conn.close()

        return redirect(url_for('view_pass'))

    return render_template('add_pass.html')


# View Pass
@app.route('/view-pass')
def view_pass():

    conn = get_db_connection()

    passes = conn.execute(
        'SELECT * FROM passes'
    ).fetchall()

    conn.close()

    return render_template(
        'view_pass.html',
        passes=passes
    )


# Pass Details After QR Scan
@app.route('/pass/<int:id>')
def pass_details(id):

    conn = get_db_connection()

    pass_data = conn.execute(
        'SELECT * FROM passes WHERE id=?',
        (id,)
    ).fetchone()

    conn.close()

    return render_template(
        'pass_details.html',
        pass_data=pass_data
    )


# Run App
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
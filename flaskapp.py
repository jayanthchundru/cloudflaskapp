from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
import sqlite3
import os
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)

# Set a secret key for session management and flashing messages
app.secret_key = 'your_secret_key_here'  # Replace with a strong secret key

# Configuration for file uploads
UPLOAD_FOLDER = '/var/www/flaskapp/uploads'
ALLOWED_EXTENSIONS = {'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize the database
def init_db():
    conn = None  # Initialize conn to None
    try:
        conn = sqlite3.connect('/var/www/flaskapp/users.db')  # Use absolute path
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (username TEXT PRIMARY KEY, password TEXT, firstname TEXT, lastname TEXT, email TEXT, address TEXT, filename TEXT, word_count INTEGER)''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:  # Only close conn if it was successfully created
            conn.close()

# Initialize the database when the app starts
init_db()

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        address = request.form['address']

        # Handle file upload
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Count words in the file
            with open(filepath, 'r') as f:
                word_count = len(f.read().split())

        # Save user details and file information to the database
        conn = None
        try:
            conn = sqlite3.connect('/var/www/flaskapp/users.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password, firstname, lastname, email, address, filename, word_count) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                      (username, password, firstname, lastname, email, address, filename, word_count))
            conn.commit()
        except sqlite3.IntegrityError:
            flash('Username already exists!')
            return redirect(request.url)
        except sqlite3.Error as e:
            flash(f'Database error: {e}')
            return redirect(request.url)
        finally:
            if conn:
                conn.close()

        return redirect(url_for('profile', username=username))
    return render_template('register.html')

# Profile page
@app.route('/profile/<username>')
def profile(username):
    conn = None
    try:
        conn = sqlite3.connect('/var/www/flaskapp/users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()
    except sqlite3.Error as e:
        flash(f'Database error: {e}')
        return redirect(url_for('index'))
    finally:
        if conn:
            conn.close()

    if user:
        return render_template('profile.html', user=user)
    flash('User not found!')
    return redirect(url_for('index'))

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = None
        try:
            conn = sqlite3.connect('/var/www/flaskapp/users.db')
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = c.fetchone()
        except sqlite3.Error as e:
            flash(f'Database error: {e}')
            return redirect(request.url)
        finally:
            if conn:
                conn.close()

        if user:
            return redirect(url_for('profile', username=username))
        flash('Invalid credentials!')
    return render_template('login.html')

# File download route
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

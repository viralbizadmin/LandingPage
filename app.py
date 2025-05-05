from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import datetime
from functools import wraps
import sqlite3
from sqlite3 import Error

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_for_testing')

# Configuration
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'securepassword123')
DATABASE_PATH = os.environ.get('DATABASE_PATH', 'submissions.db')

# Database functions
def create_connection():
    """Create a database connection to the SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        return conn
    except Error as e:
        print(e)
    return conn

def create_table():
    """Create submissions table if it doesn't exist"""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                social TEXT,
                message TEXT NOT NULL
            );
            """)
            conn.commit()
        except Error as e:
            print(e)
        finally:
            conn.close()

# Initialize database
create_table()

# Home route - serves the landing page
@app.route('/')
def index():
    return render_template('index.html')

# Process contact form submissions
@app.route('/contact', methods=['POST'])
def contact():
    if request.method == 'POST':
        # Collect form data
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone', 'Not provided')
        social = request.form.get('social', 'Not provided')
        message = request.form.get('message')
        
        # Basic validation
        if not name or not email or not message:
            flash('Please fill out all required fields.', 'error')
            return redirect(url_for('index', _anchor='contact'))
        
        # Store in database
        try:
            conn = create_connection()
            if conn:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO submissions (timestamp, name, email, phone, social, message)
                       VALUES (?, ?, ?, ?, ?, ?)""", 
                    (timestamp, name, email, phone, social, message)
                )
                conn.commit()
                conn.close()
                
                # Print the submission details to your server logs
                print("\n===== NEW FORM SUBMISSION =====")
                print(f"Name: {name}")
                print(f"Email: {email}")
                print(f"Phone: {phone}")
                print(f"Social: {social}")
                print(f"Message: {message}")
                print("================================\n")
                
                # Show success message and redirect to Calendly
                flash('Thanks for your message! Redirecting you to schedule a call...', 'success')
                
                # Replace with your actual Calendly URL
                calendly_url = "https://calendly.com/admin-viralbizsolutions/30min"
                return redirect(calendly_url)
        except Error as e:
            print(f"Database error: {e}")
            flash('There was an error processing your request. Please try again later.', 'error')
        
        return redirect(url_for('index', _anchor='contact'))

# Admin login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin login
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('admin_login.html')

# Admin dashboard
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    submissions = []
    try:
        conn = create_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM submissions ORDER BY id DESC")
            rows = cursor.fetchall()
            
            for row in rows:
                submission = {
                    'id': row[0],
                    'timestamp': row[1],
                    'name': row[2],
                    'email': row[3],
                    'phone': row[4],
                    'social': row[5],
                    'message': row[6]
                }
                submissions.append(submission)
            
            conn.close()
    except Error as e:
        print(f"Database error: {e}")
        flash('There was an error retrieving submissions.', 'error')
    
    return render_template('admin_dashboard.html', submissions=submissions)

# Admin logout
@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', None)
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 9000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_DEBUG', 'False') == 'True')

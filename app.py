from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_for_testing')

# Configuration
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'securepassword123')

# Store submissions in memory (will be lost when server restarts)
# In a production app, you'd use a database instead
submissions = []

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
        
        # Store submission with timestamp
        submission = {
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'name': name,
            'email': email,
            'phone': phone,
            'social': social,
            'message': message
        }
        submissions.insert(0, submission)  # Add to beginning of list
        
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
    return render_template('admin_dashboard.html', submissions=submissions)

# Admin logout
@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', None)
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 9000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_DEBUG', 'False') == 'True')

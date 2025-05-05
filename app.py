from flask import Flask, render_template, request, redirect, url_for, flash
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_for_testing')

Configuration (you can move this to environment variables in production)
EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS', '')  # Your email address
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')  # Your email password or app password
RECIPIENT_EMAIL = os.environ.get('RECIPIENT_EMAIL', '')  # Where to receive contact form submissions

# Home route - serves the landing page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contact', methods=['POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        social = request.form.get('social')
        message = request.form.get('message')
        
        # Basic validation
        if not name or not email or not message:
            flash('Please fill out all required fields.', 'error')
            return redirect(url_for('index', _anchor='contact'))
        
        # Send email if configured
        if EMAIL_ADDRESS and EMAIL_PASSWORD and RECIPIENT_EMAIL:
            try:
                send_email(name, email, phone, social, message)
                flash('Thank you for your message! Redirecting you to our calendar...', 'success')
            except Exception as e:
                print(f"Error sending email: {e}")
                flash('There was an error sending your message. Please try again later.', 'error')
                return redirect(url_for('index', _anchor='contact'))
        else:
            # For development without email configured
            print(f"Form submission: {name}, {email}, {phone}, {social}, {message}")
            flash('Thank you for your message! Redirecting you to our calendar...', 'success')
        
        # Redirect to Calendly after successful form submission
        calendly_url = "https://calendly.com/admin-viralbizsolutions/30min"  # Replace with your actual Calendly link
        return redirect(calendly_url)
    
def send_email(name, email, phone, social, message):
    """Send email with contact form information"""
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = f"StreetViral Contact Form: {name}"
    
    # Create email body
    body = f"""
    You have received a new contact form submission from your StreetViral website:
    
    Name: {name}
    Email: {email}
    Phone: {phone or "Not provided"}
    Social Media: {social or "Not provided"}
    
    Message:
    {message}
    
    ---
    This message was sent from the StreetViral contact form.
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Connect to SMTP server (this example uses Gmail)
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, text)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 9000))  # Changed to 9000
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_DEBUG', 'False') == 'True')

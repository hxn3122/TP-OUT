
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from functools import wraps
import requests, smtplib, random
from email.message import EmailMessage

app = Flask(__name__)
app.secret_key = 'your_secret_key'

CLIENT_ID = "97369693f40c4802a46e9da8ac150357"
CLIENT_SECRET = "180eaba8889249129208b3f332c3ee8c81dc10e692ee4e99921bf80dad1d1530"
CALLBACK_SECRET = "ecb05339da134d048c3c4962b6342c17"
AUTH_URL = "https://identity.tappayy.com/token"
PAYOUT_URL = "https://gateway.tappayy.com/tappay/payout/ibft"

OTP_EMAIL = "mianshahbir124@gmail.com"
OTP_EMAIL_PASSWORD = "scwa snrq kxwd aown"
AUTHORIZED_EMAIL = "flaskrender34@gmail.com"
otp_code = None

def send_otp_email(target_email, code):
    msg = EmailMessage()
    msg.set_content(f"Your OTP for login is: {code}")
    msg['Subject'] = 'Your TapPay Admin OTP'
    msg['From'] = OTP_EMAIL
    msg['To'] = target_email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(OTP_EMAIL, OTP_EMAIL_PASSWORD)
        smtp.send_message(msg)

def get_access_token():
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(AUTH_URL, data=data, headers=headers)
    if response.status_code == 200:
        return response.json().get('access_token')
    return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return redirect(url_for('welcome'))

@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    global otp_code
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in ['mianhasan3122@gmail.com', 'hxnsticx@gmail.com', 'flaskrender34@gmail.com'] and password == 'hxnlinks@1735':
            otp_code = str(random.randint(100000, 999999))
            session['user_email'] = email
            send_otp_email(email, otp_code)
            session.permanent = False
            session['pending_otp'] = True
            return redirect(url_for('verify_otp'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    global otp_code
    if 'pending_otp' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        input_otp = request.form['otp']
        if input_otp == otp_code:
            session.pop('pending_otp', None)
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template('verify_otp.html', error='Incorrect OTP')
    return render_template('verify_otp.html')

@app.route('/resend_otp', methods=['POST'])
def resend_otp():
    global otp_code
    if 'user_email' not in session:
        return redirect(url_for('login'))

    otp_code = str(random.randint(100000, 999999))
    send_otp_email(session['user_email'], otp_code)
    session['pending_otp'] = True
    return redirect(url_for('verify_otp'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        data = request.form.to_dict()
        data['amount'] = float(data['amount'])
        data['currency'] = "PKR"
        token = get_access_token()
        if not token:
            return "Error retrieving access token"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        response = requests.post(PAYOUT_URL, headers=headers, json=data)
        return jsonify(response.json())
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

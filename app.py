
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from functools import wraps
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'

CLIENT_ID = "97369693f40c4802a46e9da8ac150357"
CLIENT_SECRET = "180eaba8889249129208b3f332c3ee8c81dc10e692ee4e99921bf80dad1d1530"
CALLBACK_SECRET = "ecb05339da134d048c3c4962b6342c17"
AUTH_URL = "https://identity.tappayy.com/token"
PAYOUT_URL = "https://gateway.tappayy.com/tappay/payout/ibft"

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

# Login protection decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'hxnlinks@1735':
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        merchantTransactionId = request.form['merchantTransactionId']
        billRefNo = request.form['billRefNo']
        amount = float(request.form['amount'])
        consumerNo = request.form['consumerNo']
        mobileNo = request.form['mobileNo']
        accountTitle = request.form['accountTitle']
        payeeName = request.form['payeeName']
        purchaseItem = request.form['purchaseItem']
        payeeCNIC = request.form['payeeCNIC']
        payeeEmail = request.form['payeeEmail']
        bankCode = request.form['bankCode']
        vendorCode = request.form['vendorCode']

        token = get_access_token()
        if not token:
            return "Error retrieving access token"

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        payload = {
            "merchantTransactionId": merchantTransactionId,
            "billRefNo": billRefNo,
            "amount": amount,
            "consumerNo": consumerNo,
            "mobileNo": mobileNo,
            "accountTitle": accountTitle,
            "payeeName": payeeName,
            "purchaseItem": purchaseItem,
            "payeeCNIC": payeeCNIC,
            "payeeEmail": payeeEmail,
            "currency": "PKR",
            "bankCode": bankCode,
            "vendorCode": vendorCode
        }

        response = requests.post(PAYOUT_URL, headers=headers, json=payload)
        return jsonify(response.json())

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

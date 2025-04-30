from flask import Flask, render_template, request, redirect, url_for, session
import json

app = Flask(__name__)
app.secret_key = 'secret'  # Needed for session

# Load fake user data
def load_users():
    with open('users.json') as f:
        return json.load(f)

# Load account data
def load_data():
    with open('data.json') as f:
        return json.load(f)

def save_data(data):
    with open('data.json', 'w') as f:
        json.dump(data, f)

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()
        if username in users and users[username] == password:
            session['user'] = username
            return redirect('/dashboard')
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    data = load_data().get(session['user'], {})
    return render_template('dashboard.html', accounts=data)

@app.route('/add', methods=['GET', 'POST'])
def add_account():
    if 'user' not in session:
        return redirect('/login')
    if request.method == 'POST':
        nickname = request.form['nickname']
        acc_type = request.form['type']
        balance = request.form['balance']

        all_data = load_data()
        user_data = all_data.get(session['user'], [])
        user_data.append({'nickname': nickname, 'type': acc_type, 'balance': balance})
        all_data[session['user']] = user_data
        save_data(all_data)
        return redirect('/dashboard')
    return render_template('add_account.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)

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
        json.dump(data, f, indent = 4)

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()

        if username in users and users[username]['password'] == password:
            session['user'] = username
            return redirect('/dashboard')
        else:
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    username = session['user']
    users = load_users()
    name = users[username]['name']
    data = load_data().get(username, [])
    show_balance = request.args.get('show_balance', 'yes')
    return render_template('dashboard.html', accounts=data, name=name, show_balance=show_balance)


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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        
        users = load_users()
        if username in users:
            return render_template('register.html', error='Username already taken.')

        users[username] = {"name": name, "password": password}
        with open('users.json', 'w') as f:
            json.dump(users, f, indent=4)

        return redirect('/login')
    return render_template('register.html')

@app.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user' not in session:
        return redirect('/login')
    
    users = load_users()
    username = session['user']
    user_info = users[username]

    if request.method == 'POST':
        new_name = request.form['name']
        new_password = request.form['password']
        users[username]['name'] = new_name
        users[username]['password'] = new_password
        with open('users.json', 'w') as f:
            json.dump(users, f)
        return redirect('/dashboard')

    return render_template('edit_profile.html', name=user_info['name'], password=user_info['password'])

@app.route('/delete-profile', methods=['POST'])
def delete_profile():
    if 'user' not in session:
        return redirect('/login')

    username = session['user']
    users = load_users()
    data = load_data()

    users.pop(username, None)
    data.pop(username, None)

    with open('users.json', 'w') as f:
        json.dump(users, f)
    with open('data.json', 'w') as f:
        json.dump(data, f)

    session.clear()
    return redirect('/login')

@app.route('/edit-account', methods=['GET', 'POST'])
def edit_account():
    if 'user' not in session:
        return redirect('/login')

    username = session['user']
    all_data = load_data()
    user_accounts = all_data.get(username, [])

    if request.method == 'POST':
        original_nickname = request.form['original_nickname']
        new_nickname = request.form['nickname']
        acc_type = request.form['type']
        balance = request.form['balance']

        # Update the account
        for account in user_accounts:
            if account['nickname'] == original_nickname:
                account['nickname'] = new_nickname
                account['type'] = acc_type
                account['balance'] = balance
                break

        all_data[username] = user_accounts
        save_data(all_data)
        return redirect('/dashboard')

    # GET method — show the form
    nickname = request.args.get('nickname')
    account_to_edit = next((a for a in user_accounts if a['nickname'] == nickname), None)

    if not account_to_edit:
        return "<h2>Account not found</h2><a href='/dashboard'>Return to Dashboard</a>"

    return render_template('edit_account.html', account=account_to_edit)

@app.route('/delete-account', methods=['POST'])
def delete_account():
    if 'user' not in session:
        return redirect('/login')

    username = session['user']
    nickname = request.form['nickname']
    all_data = load_data()
    user_accounts = all_data.get(username, [])

    # Filter out the account
    user_accounts = [acc for acc in user_accounts if acc['nickname'] != nickname]
    all_data[username] = user_accounts
    save_data(all_data)

    return redirect('/dashboard')

@app.route('/delete-selected', methods=['POST'])
def delete_selected():
    if 'user' not in session:
        return redirect('/login')

    username = session['user']
    selected = request.form.getlist('selected_accounts')  # Get list of nicknames
    all_data = load_data()
    user_accounts = all_data.get(username, [])

    # Filter out selected accounts
    updated_accounts = [acc for acc in user_accounts if acc['nickname'] not in selected]
    all_data[username] = updated_accounts
    save_data(all_data)

    return redirect('/dashboard')


if __name__ == '__main__':
    app.run(debug=True)

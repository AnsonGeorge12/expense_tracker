from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "my_secret_key_123"  # Required for login sessions

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="expense_db"
    )
# ... (keep your existing imports and get_db function) ...

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    db = get_db()
    cursor = db.cursor()
    try:
        # Simply insert the user
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        db.commit()
        # After registering, we tell them it worked and provide a link back to the login
        return "Account created! <a href='/'>Click here to login</a>"
    except:
        return "Error: Username might be taken. <a href='/'>Try again</a>"
    finally:
        db.close()

# Keep your existing /login, /dashboard, /add, and /logout routes as they are
# 1. HOME PAGE (LOGIN)
@app.route('/')
def home():
    return render_template('login.html')

# 2. LOGIN LOGIC
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT user_id FROM users WHERE username=%s AND password=%s",
        (username, password)
    )
    user = cursor.fetchone()
    db.close()

    if user:
        session['user_id'] = user[0]
        return redirect('/dashboard')
    else:
        return "Invalid Login! <a href='/'>Try again</a>"

# 3. DASHBOARD
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')

    db = get_db()
    cursor = db.cursor()
    
    # Query 1: Get all individual expenses
    cursor.execute("SELECT * FROM expenses WHERE user_id=%s", (session['user_id'],))
    data = cursor.fetchall()
    
    # Query 2: Get the total sum for this user
    cursor.execute("SELECT SUM(amount) FROM expenses WHERE user_id=%s", (session['user_id'],))
    total_sum = cursor.fetchone()[0]
    
    # If the user has no expenses, total_sum will be None. Change it to 0.
    if total_sum is None:
        total_sum = 0
        
    db.close()

    return render_template('dashboard.html', expenses=data, total=total_sum)

# 4. ADD EXPENSE
@app.route('/add', methods=['POST'])
def add():
    if 'user_id' not in session:
        return redirect('/')

    item = request.form['item']
    amt = request.form['amount']
    cat = request.form['category']

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO expenses (user_id, item_name, amount, category) VALUES (%s, %s, %s, %s)",
        (session['user_id'], item, amt, cat)
    )
    db.commit()
    db.close()

    return redirect('/dashboard')

# 5. LOGOUT
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "my_secret_key_123"

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="expense_db"
    )

# HOME PAGE (LOGIN)
@app.route('/')
def home():
    return render_template('login.html')

# REGISTER
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, password)
        )
        db.commit()
        return "Account created! <a href='/'>Click here to login</a>"
    except:
        return "Error: Username might be taken. <a href='/'>Try again</a>"
    finally:
        db.close()

# LOGIN
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

# DASHBOARD
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')

    db = get_db()
    cursor = db.cursor()

    # All expenses
    cursor.execute(
        "SELECT * FROM expenses WHERE user_id=%s",
        (session['user_id'],)
    )
    data = cursor.fetchall()

    # Total sum
    cursor.execute(
        "SELECT SUM(amount) FROM expenses WHERE user_id=%s",
        (session['user_id'],)
    )
    total_sum = cursor.fetchone()[0]
    if total_sum is None:
        total_sum = 0

    # Category-wise summary (OPTIONAL)
    cursor.execute(
        "SELECT category, SUM(amount) FROM expenses WHERE user_id=%s GROUP BY category",
        (session['user_id'],)
    )
    category_totals = cursor.fetchall()

    db.close()

    return render_template(
        'dashboard.html',
        expenses=data,
        total=total_sum,
        category_totals=category_totals
    )

# ADD EXPENSE
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

# DELETE EXPENSE (OPTIONAL)
@app.route('/delete/<int:expense_id>')
def delete_expense(expense_id):
    if 'user_id' not in session:
        return redirect('/')

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "DELETE FROM expenses WHERE expense_id=%s AND user_id=%s",
        (expense_id, session['user_id'])
    )
    db.commit()
    db.close()

    return redirect('/dashboard')

# LOGOUT
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
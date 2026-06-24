from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "food_donation_secret_2026"

# ===========================
# DATABASE INIT
# ===========================
def init_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS donations(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        food TEXT,
        quantity TEXT,
        location TEXT,
        phone TEXT,
        address TEXT,
        expiry TEXT,
        latitude TEXT,
        longitude TEXT,
        accepted INTEGER DEFAULT 0,
        receiver_name TEXT,
        receiver_phone TEXT,
        receiver_address TEXT
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    ''')

    conn.commit()
    conn.close()

init_db()

# ===========================
# HOME
# ===========================
@app.route('/')
def home():
    return render_template('welcome.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

# ===========================
# DONATE
# ===========================
@app.route('/donate', methods=['GET', 'POST'])
def donate():
    if request.method == 'POST':
        name = request.form['name']
        food = request.form['food']
        quantity = request.form['quantity']
        location = request.form['location']
        phone = request.form['phone']
        address = request.form['address']
        expiry = request.form['expiry']

        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute('''
        INSERT INTO donations
        (name, food, quantity, location, phone, address, expiry, latitude, longitude)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, food, quantity, location, phone, address, expiry, latitude, longitude))

        conn.commit()
        conn.close()

        return redirect('/view')

    return render_template('donate.html')

# ===========================
# VIEW DONATIONS
# ===========================
@app.route('/view')
def view():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    # show ONLY NOT accepted donations
    cur.execute("SELECT * FROM donations WHERE accepted=0")
    donations = cur.fetchall()

    # count pending donations only
    cur.execute("SELECT COUNT(*) FROM donations WHERE accepted=0")
    count = cur.fetchone()[0]

    conn.close()

    return render_template('view.html', donations=donations, count=count)
# ===========================
# DELETE
# ===========================
@app.route('/delete/<int:id>')
def delete(id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute("DELETE FROM donations WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/view')

# ===========================
# ACCEPT PAGE
# ===========================
@app.route('/accept/<int:donation_id>')
def accept_food(donation_id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute("SELECT * FROM donations WHERE id=?", (donation_id,))
    donation = cur.fetchone()

    conn.close()

    return render_template('accept.html', donation=donation)

# ===========================
# CONFIRM ACCEPT
# ===========================
@app.route('/confirm_accept/<int:donation_id>', methods=['POST'])
def confirm_accept(donation_id):

    receiver_name = request.form['receiver_name']
    receiver_phone = request.form['receiver_phone']
    receiver_address = request.form['receiver_address']

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute('''
    UPDATE donations
    SET accepted=1,
        receiver_name=?,
        receiver_phone=?,
        receiver_address=?
    WHERE id=?
    ''', (receiver_name, receiver_phone, receiver_address, donation_id))

    conn.commit()
    conn.close()

    return redirect('/accepted')

# ===========================
# ACCEPTED PAGE
# ===========================
@app.route('/accepted')
def accepted():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute("SELECT * FROM donations WHERE accepted=1")
    donations = cur.fetchall()

    conn.close()

    return render_template('accepted.html', donations=donations)

# ===========================
# SIGNUP
# ===========================
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))

        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('signup.html')

# ===========================
# LOGIN
# ===========================
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cur.fetchone()

        conn.close()

        if user:
            session['username'] = username
            return redirect('/')
        else:
            return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')

# ===========================
# PROFILE
# ===========================
@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect('/login')

    username = session['username']

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cur.fetchone()

    cur.execute("SELECT * FROM donations WHERE name=?", (username,))
    donations = cur.fetchall()

    cur.execute("SELECT * FROM donations WHERE receiver_name=?", (username,))
    received = cur.fetchall()

    conn.close()

    return render_template('profile.html',
                           user=user,
                           donations=donations,
                           received=received)

# ===========================
# LOGOUT
# ===========================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ===========================
# RUN APP
# ===========================
if __name__ == '__main__':
    app.run(debug=True)

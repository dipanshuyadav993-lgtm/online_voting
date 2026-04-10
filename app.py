from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# DATABASE CREATE
conn = sqlite3.connect('database.db')
c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS users (name TEXT, voter_id TEXT, fingerprint TEXT, face TEXT, voted INTEGER)")
c.execute("CREATE TABLE IF NOT EXISTS votes (candidate TEXT)")

conn.commit()
conn.close()

# HOME
@app.route('/')
def home():
    return render_template('login.html')

# REGISTER
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        voter_id = request.form['voter_id']
        fingerprint = request.form['fingerprint']
        face = request.form['face']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("INSERT INTO users VALUES (?,?,?,?,0)", (name, voter_id, fingerprint, face))

        conn.commit()
        conn.close()

        return redirect('/')
    
    return render_template('register.html')

# LOGIN
@app.route('/login', methods=['POST'])
def login():
    voter_id = request.form['voter_id']

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    user = c.execute("SELECT * FROM users WHERE voter_id=?", (voter_id,)).fetchone()
    conn.close()

    if user:
        if user[4] == 1:
            return "You already voted ❌"
        return redirect(f'/fingerprint/{voter_id}')
    
    return "User not found"

# FINGERPRINT
@app.route('/fingerprint/<voter_id>', methods=['GET','POST'])
def fingerprint(voter_id):
    if request.method == 'POST':
        fp = request.form['fingerprint']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        user = c.execute("SELECT * FROM users WHERE voter_id=?", (voter_id,)).fetchone()

        if user and user[2] == fp:
            return redirect(f'/face/{voter_id}')
        else:
            return "Fingerprint Wrong ❌"

    return render_template('fingerprint.html')

# FACE
@app.route('/face/<voter_id>', methods=['GET','POST'])
def face(voter_id):
    if request.method == 'POST':
        face_input = request.form['face']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        user = c.execute("SELECT * FROM users WHERE voter_id=?", (voter_id,)).fetchone()

        if user and user[3] == face_input:
            return redirect(f'/vote/{voter_id}')
        else:
            return "Face Not Matched ❌"

    return render_template('face.html')

# VOTE
@app.route('/vote/<voter_id>', methods=['GET','POST'])
def vote(voter_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    user = c.execute("SELECT * FROM users WHERE voter_id=?", (voter_id,)).fetchone()

    # अगर पहले vote कर चुका है
    if user[4] == 1:
        conn.close()
        return "You already voted ❌"

    if request.method == 'POST':
        candidate = request.form['candidate']

        c.execute("INSERT INTO votes VALUES (?)", (candidate,))
        c.execute("UPDATE users SET voted=1 WHERE voter_id=?", (voter_id,))

        conn.commit()
        conn.close()

        return redirect('/result')

    conn.close()
    return render_template('vote.html')

# RESULT
@app.route('/result')
def result():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    data = c.execute("SELECT candidate, COUNT(*) FROM votes GROUP BY candidate").fetchall()

    conn.close()
    return render_template('result.html', data=data)

# RUN SERVER (LAST LINE)
app.run(debug=True)
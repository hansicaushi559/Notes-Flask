from flask import Flask, render_template, redirect, request, session, flash, jsonify
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
from auth import login_required


app = Flask(__name__)
app.secret_key = 'your_secret_key'

db = pymysql.connect(
    host='localhost',
    user='root',
    password='hansi',
    database='project'
)

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
Session(app)



@app.route('/', methods=['POST','GET'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')
        user_id = session['user_id']
        # Save that note in db
        cur = db.cursor()
        query = "INSERT INTO notes (note, user_id) VALUES (%s, %s)"
        cur.execute(query, (note, user_id))
        db.commit()
        cur.close()
        return redirect('/notes')
    else:
        return render_template('home.html')


@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        if not username:
            flash("Missing username", category="error")
            return redirect('/signup')
        password1 = request.form.get('password1')
        if not password1:
            flash("Missing password", category="error")
            return redirect('/signup')
        password2 = request.form.get('password2')
        if not password2:
            flash("Missing password confirmation", category="error")
            return redirect('/signup')
        if password1 != password2:
            flash("Passwords are not the same", category="error")
            return redirect('/signup')
            
        hash_password = generate_password_hash(password1)
        cur = db.cursor()
        cur.execute('INSERT INTO users (username, hash) VALUES(%s, %s)', (username, hash_password))
        db.commit()
        cur.close()
        return redirect('/login')
    else:   
        return render_template('signup.html')

@app.route('/notes')
def notes():
    user_id = session['user_id']
    cur = db.cursor()
    query = 'SELECT * FROM notes WHERE user_id = %s'
    cur.execute(query, (user_id))
    result = cur.fetchall()
    print(result)
    return render_template('notes.html', notes = result)
    

@app.route('/logout')
def logout():
    session.clear()
    return redirect("/login")



@app.route('/login', methods=['POST','GET'])
def login():

    if request.method == 'POST':
       username = request.form.get("username")
       if not username:
        flash("Missing username", category="error")
        return redirect('/login')

       password = request.form.get("password")
       if not password:
           flash("Missing username", category="error")
           return redirect('/login')
       

       cur = db.cursor()
       cur.execute("SELECT id, hash FROM users WHERE username = %s", (username))
       result = cur.fetchone()

       if result and check_password_hash(result[1], password):
            session['user_id'] = result[0]
            flash("You logged-in successfully", category="success")
            return redirect("/")
       else:
           flash("Username or password is incorrect", category="error")
           return redirect("/login")
    else:
        return render_template('login.html')
    
@app.route('/notes/delete/<string:id>', methods=['GET'])
def delete_note(id):
    cur = db.cursor()
    query = 'DELETE FROM notes WHERE id = %s'
    cur.execute(query, (id))
    db.commit()
    return redirect('/notes')


if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import hashlib
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)


def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  email TEXT NOT NULL,
                  password TEXT NOT NULL)''')
    conn.commit()
    conn.close()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def get_user_by_username(username):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()
        return user
    except Exception as e:
        print(e)
        return None


def get_user_by_username_and_password(username, password):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        hashed = hash_password(password)
        c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed))
        user = c.fetchone()
        conn.close()
        return user
    except Exception as e:
        print(e)
        return None


def create_user(username, email, password):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        hashed = hash_password(password)
        c.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                  (username, email, hashed))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        print(e)
        return False


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('devduck'))
    return redirect(url_for('register'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            confirm_password = request.form['confirm_password']

            if password != confirm_password:
                return render_template('register.html', error='Пароли не совпадают')

            if create_user(username, email, password):
                user = get_user_by_username(username)
                session['user_id'] = user[0]
                session['username'] = user[1]
                session['email'] = user[2]
                return redirect(url_for('devduck'))
            else:
                return render_template('register.html', error='Пользователь с таким никнеймом уже существует')
        except Exception as e:
            print(e)
            return render_template('register.html', error='Ошибка регистрации')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']

            user = get_user_by_username_and_password(username, password)
            if user:
                session['user_id'] = user[0]
                session['username'] = user[1]
                session['email'] = user[2]
                return redirect(url_for('devduck'))
            else:
                return render_template('login.html', error='Неверный никнейм или пароль')
        except Exception as e:
            print(e)
            return render_template('login.html', error='Ошибка входа')

    return render_template('login.html')


@app.route('/devduck')
def devduck():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('devduck.html', username=session.get('username'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=8080)
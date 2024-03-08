from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2.extras
import psycopg2
import re

app = Flask(__name__)

app.secret_key = "bernardomuse"


def get_db_connection():
    return psycopg2.connect(host='localhost', database='items', user='postgres', password='5599emoyo')


@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    s = 'SELECT * FROM item2'
    cur.execute(s)
    item_list = cur.fetchall()
    # cur.close()
    # conn.close()
    return render_template('index.html', item_list=item_list)


@app.route("/add_item", methods=["GET", "POST"])
def add_item():
    if request.method != "POST":
        return
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM item2')
    name = request.form["name"]
    barcode = request.form["barcode"]
    price = request.form["price"]
    description = request.form["description"]

    cur.execute(
        "INSERT INTO item2(name, barcode, price, description) VALUES(%s,%s,%s,%s)", (name, barcode, price, description))
    conn.commit()
    flash('Item added successful')
    return redirect(url_for('index'))


@app.route("/edit/<id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM item2 WHERE id = %s', (id))
    data = cur.fetchall()
    cur.close()
    print(data[0])
    return render_template('edit.html', item2=data[0])


@app.route("/update/<id>", methods=["GET", "POST"])
def update(id):
    if request.method != "POST":
        return render_template('index.html')
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM item2')
    name = request.form["name"]
    barcode = request.form["barcode"]
    price = request.form["price"]
    description = request.form["description"]

    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
                    UPDATE item2
                    SET     name=%s, 
                            barcode=%s, 
                            price=%s,
                            description=%s,                         
                    WHERE id= %s,
                """, (name, barcode, price, description, id))
    flash("update was successful")
    conn.commit()
    return redirect(url_for('index'))


@app.route('/delete/<string:id>', methods=['GET', 'POST'])
def delete(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('DELETE FROM item2 WHERE id={0}'.format(id))
    conn.commit()
    flash('Successfully deleted')
    return redirect(url_for("index"))


@app.route('/register', methods=['POST', 'GET'])
def register():
    conn = get_db_connection()
    if request.method != 'POST' or 'name' not in request.form or 'email' not in request.form or 'password' not in request.form or 'confirm_password' not in request.form:
        return render_template('register.html')
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    _hashed_password = generate_password_hash(password)

    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    s = ("SELECT * FROM signup WHERE name=%s", (name))
    cur.execute(s)
    account = cur.fetchone()
    print(account)

    if account:
        flash('account exists')
    elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        flash('invalid email address')
    elif not re.match(r"[A-Za-z0-9]+", name):
        flash('user must have 1 character')
    elif not name or not password or not email:
        flash('fill the form')
    else:
        cur.execute("INSERT INTO login(name,email,password,confirm_password)VALUES(%s,%s,%s,%s)",
                    (name, email, password, confirm_password, _hashed_password))
        conn.commit()
        flash('Item successful')


@app.route('/login', methods=['POST', 'GET'])
def login():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method != 'POST' or 'email' not in request.form or request.form or 'password' not in request.form:
        return render_template('login.html')
    # name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    s = ('SELECT * FROM login1 WHERE email=%s', (email))
    cur.execute(s)

    if account := cur.fetchone():
        password_rs = account['password']
        print(password_rs)
        if check_password_hash(password_rs, password):
            session['logged in'] = True
            session['id'] = account['id']
            session['email'] = account['email']
            return redirect(url_for('home'))
        else:
            flash('incorrect name/password')
    else:
        flash('incorrect username/password')


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('name', None)
    return redirect(url_for("login"))


if __name__ == '__main__':
    app.run(debug=True)

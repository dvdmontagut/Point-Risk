from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from email.message import EmailMessage
import ssl
import smtplib
import string
import random
import requests
import json
import pymysql
import os

app = Flask(__name__)
app.secret_key = 'qwerty123'


def get_con():
    return pymysql.connect(host='172.17.0.2', user='root', password='admin123', db='par')


@app.route('/PAR/logout/')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('email', None)
    session.pop('pass', None)
    # Redirect to login page
    return redirect(url_for('login'))


@app.route("/PAR/confirm/<string:token>", methods=['GET'])
def confirm(token):
    con = get_con()
    with con:
        with con.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM users WHERE token LIKE %s "
            number = cursor.execute(sql, token)
            if number != 0:
                result = cursor.fetchone()
                if result["active"] == 1:
                    return redirect(url_for('.login', msg=4))

                sql = "UPDATE users SET active=1 WHERE token LIKE %s"
                cursor.execute(sql, token)
                con.commit()
                return redirect(url_for('.login', msg=2))

            else:
                return redirect(url_for('.login', msg=3))


@app.route("/PAR/login/", methods=['POST', 'GET'])
@app.route("/PAR/login/<int:msg>", methods=['POST', 'GET'])
def login(msg=0):
    if request.method == 'GET':
        if msg == 1:
            return render_template('noLog/login.html', msg="Check your mail to confirm your account.")
        elif msg == 2:
            return render_template('noLog/login.html', msg="Account confirmed.")
        elif msg == 3:
            return render_template('noLog/login.html', warning="Data incorrect.")
        elif msg == 4:
            return render_template('noLog/login.html', warning="Account already confirmed.")
        elif msg == 5:
            return render_template('noLog/login.html', warning="You have to Log In")
        elif msg == 6:
            return render_template('noLog/login.html', warning="You have to confirm your account first")
        else:
            return render_template('noLog/login.html')

    email = request.form.get('email')
    password = request.form.get('pass')
    con = get_con()
    with con:
        with con.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM users WHERE email LIKE %s "
            number = cursor.execute(sql, email)
            if number == 0:
                return redirect(url_for('.login', msg=3))
            else:
                res = cursor.fetchone()
                if res["active"] == 0:
                    return redirect(url_for('.login', msg=6))
                if not check_password_hash(res["password"], password):
                    return redirect(url_for('.login', msg=3))
                else:
                    session['loggedin'] = True
                    session['id'] = res['id']
                    session['username'] = res['username']
                    session['email'] = res['email']
                    session['pass'] = res['password']
                    return redirect(url_for('.profile'))


@app.route("/PAR/changePass/", methods=['POST', 'GET'])
def changePass():
    if 'loggedin' in session:
        if request.method == 'GET':
            return render_template('profile/changePass.html')

        npass = request.form.get('npass')
        opass = request.form.get('opass')
        con = get_con()
        with con:
            with con.cursor(pymysql.cursors.DictCursor) as cursor:
                if not check_password_hash(session['pass'], opass):
                    return render_template('profile/changePass.html', warning="Wrong Password")
                else:
                    sql = "UPDATE users SET password = %s WHERE email LIKE %s"
                    cursor.execute(sql, (generate_password_hash(npass, method='sha256'), session['email']))
                    con.commit()

    return redirect(url_for('.profile'))


@app.route("/PAR/register/", methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('noLog/registration.html')

    email = request.form.get('email')
    name = request.form.get('username')
    password = request.form.get('pass')
    con = get_con()
    with con:
        with con.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM users WHERE email LIKE %s OR username LIKE %s "
            number = cursor.execute(sql, (email, name))
            if number != 0:
                return render_template('noLog/registration.html', warning="Data already exists")
            else:
                check = True
                while check:
                    res = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
                    sql = "SELECT * FROM users WHERE token LIKE %s"
                    if cursor.execute(sql, res) == 0:
                        check = False

                sql = "INSERT INTO users (username, email, password, active, role, token) VALUES (%s, %s, %s, 0, 'user', %s)"
                number = cursor.execute(sql, (name, email, generate_password_hash(password, method='sha256'), res))
                if number == 1:
                    email_sender = 'pointarisk@gmail.com'
                    email_password = 'orsntrooqzvucoim'
                    email_receiver = email
                    subject = 'Confirm email Point and Risk'
                    body = f"Use this link: http://localhost:5001/PAR/confirm/{res}"
                    em = EmailMessage()
                    em['From'] = email_sender
                    em['To'] = email_receiver
                    em['Subject'] = subject
                    em.set_content(body)
                    context = ssl.create_default_context()
                    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                        smtp.login(email_sender, email_password)
                        smtp.sendmail(email_sender, email_receiver, em.as_string())

                    con.commit()

    return redirect(url_for('.login', msg=1))


@app.route("/PAR/forgot/", methods=['POST', 'GET'])
def forgot():
    if request.method == 'GET':
        return render_template('noLog/forgot.html')

    email = request.form.get('email')
    con = get_con()
    with con:
        with con.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM users WHERE email LIKE %s  "
            number = cursor.execute(sql, email)
            if number == 0:
                return redirect(url_for('.login'))
            else:
                res = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
                sql = "UPDATE users SET password = %s WHERE email LIKE %s"
                cursor.execute(sql, (generate_password_hash(res, method='sha256'), email))
                con.commit()
                email_sender = 'pointarisk@gmail.com'
                email_password = 'orsntrooqzvucoim'
                email_receiver = email
                subject = 'Password Change'
                body = f"Your new password is: {res} \n Go to the web http://localhost:5001/PAR/login/ "
                em = EmailMessage()
                em['From'] = email_sender
                em['To'] = email_receiver
                em['Subject'] = subject
                em.set_content(body)
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                    smtp.login(email_sender, email_password)
                    smtp.sendmail(email_sender, email_receiver, em.as_string())

                return redirect(url_for('.login'))


@app.route("/db/")
def conect():
    con = get_con()
    verdad = con.open
    return render_template('conexion.html', verdad=verdad)


@app.route("/PAR/profile")
def profile():
    if 'loggedin' in session:
        con = get_con()
        with con:
            with con.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = "SELECT * FROM risks WHERE user_id = %s  "
                numberR = cursor.execute(sql, session['id'])
                sql = "SELECT * FROM tables WHERE user_id = %s  "
                numberT = cursor.execute(sql, session['id'])
        return render_template('profile/profile.html', username=session['username'], email=session['email'],
                               risks=numberR,
                               tables=numberT)

    return redirect(url_for('.login', msg=5))


@app.route("/PAR/risks")
def risks():
    if 'loggedin' in session:
        con = get_con()
        with con:
            with con.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = "SELECT * FROM risks WHERE user_id = %s  "
                numberR = cursor.execute(sql, session['id'])
                risks = cursor.fetchall()
                # return f"{numberR}{risks} asi es doña"
        return render_template('risks/riskIndex.html', numberR=numberR, risks=risks)

    return redirect(url_for('.login', msg=5))


@app.route("/PAR/risks/create", methods=['POST', 'GET'])
def risksCreate():
    if 'loggedin' in session:
        if request.method == "GET":
            return render_template('risks/riskCreate.html')

        name = request.form.get('name')
        cat = request.form.get('cat')
        description = request.form.get('description')
        public = request.form.get('public')
        if public:
            public = 1
        else:
            public = 0

        con = get_con()
        with con:
            with con.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = "INSERT INTO risks (name, category, descript, public, user_id) VALUES (%s, %s, %s, %s, %s)"
                number = cursor.execute(sql, (name, cat, description, public, session["id"]))
                con.commit()

        return redirect(url_for('.risks'))

    return redirect(url_for('.login', msg=5))


@app.route("/PAR/tables", methods=['POST', 'GET'])
def tables():
    if 'loggedin' in session:
        con = get_con()
        if request.method == 'POST':
            name = request.form.get("name")
            type = request.form.get("type")
            with con:
                with con.cursor(pymysql.cursors.DictCursor) as cursor:
                    sql = "INSERT INTO tables (user_id, name) VALUES (%s, %s)"
                    number = cursor.execute(sql, (session["id"], name))
                    if type == "fast":
                        sql = "SELECT * FROM tables WHERE user_id = %s AND name = %s"
                        number = cursor.execute(sql, (session["id"], name))
                        tableId = cursor.fetchone()["id"]
                        sql = "SELECT * FROM risks WHERE user_id = 1"
                        numberR = cursor.execute(sql)
                        risks = cursor.fetchall()
                        for risk in risks:
                            sql = "INSERT INTO trows (table_id, risk_id) values (%s, %s)"
                            cursor.execute(sql, (tableId, risk["id"]))

                    sql = "SELECT * FROM tables WHERE user_id = %s  "
                    numberT = cursor.execute(sql, session['id'])
                    tables = cursor.fetchall()
                    con.commit()
                    return render_template('tables/tablesIndex.html', numberT=numberT, tables=tables)
        with con:
            with con.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = "SELECT * FROM tables WHERE user_id = %s  "
                numberT = cursor.execute(sql, session['id'])
                tables = cursor.fetchall()
                # return f"{numberR}{risks} asi es doña"
        return render_template('tables/tablesIndex.html', numberT=numberT, tables=tables)

    return redirect(url_for('.login', msg=5))


@app.route("/PAR/tables/delete/<int:id>", methods=['GET'])
def tablesDelete(id):
    if 'loggedin' in session:
        con = get_con()
        with con:
            with con.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = 'DELETE FROM tables WHERE user_id = %s AND id = %s'
                number = cursor.execute(sql, (session["id"], id))
                con.commit()

        return redirect(url_for('.tables'))

    return redirect(url_for('.login', msg=5))


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

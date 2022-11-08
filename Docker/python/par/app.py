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
            return render_template('login.html', msg="Check your mail to confirm your account.")
        elif msg == 2:
            return render_template('login.html', msg="Account confirmed.")
        elif msg == 3:
            return render_template('login.html', warning="Data incorrect.")
        elif msg == 4:
            return render_template('login.html', warning="Account already confirmed.")
        elif msg == 5:
            return render_template('login.html', warning="You have to Log In")
        else:
            return render_template('login.html')

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
                if not check_password_hash(res["password"], password):
                    return redirect(url_for('.login', msg=3))
                else:
                    session['loggedin'] = True
                    session['id'] = res['id']
                    session['username'] = res['username']
                    session['email'] = res['email']
                    session['pass'] = res['password']
                    return redirect(url_for('.profile'))


@app.route("/PAR/register/", methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('registration.html')

    email = request.form.get('email')
    name = request.form.get('username')
    password = request.form.get('pass')
    con = get_con()
    with con:
        with con.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM users WHERE email LIKE %s OR username LIKE %s "
            number = cursor.execute(sql, (email, name))
            if number != 0:
                return render_template('registration.html', warning="Data already exists")
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
        return render_template('forgot.html')

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
        return render_template('profile.html', name=session['username'])

    return redirect(url_for('.login', msg=5))


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

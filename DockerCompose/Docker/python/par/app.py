from flask import Flask, render_template, request, redirect, url_for, session, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from email.message import EmailMessage
import ssl
import smtplib
import pdfkit
import string
import random
import pymysql
import os
import sys

app = Flask(__name__)
app.secret_key = 'qwerty123'


def get_con():
    return pymysql.connect(host='db', user='root', password='admin123', db='par')


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


@app.route("/PAR//", methods=['POST', 'GET'])
@app.route("/", methods=['POST', 'GET'])
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
                sql = "SELECT * FROM risks WHERE user_id = %s ORDER BY id DESC "
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


@app.route("/PAR/risks/delete/<int:id>", methods=['GET'])
def risksDelete(id):
    if 'loggedin' in session:
        con = get_con()
        with con:
            with con.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = 'DELETE FROM risks WHERE user_id = %s AND id = %s'
                number = cursor.execute(sql, (session["id"], id))
                con.commit()

        return redirect(url_for('.risks'))

    return redirect(url_for('.login', msg=5))


@app.route("/PAR/risks/copy/<int:id>", methods=['GET'])
def risksCopy(id):
    if 'loggedin' in session:
        con = get_con()
        with con:
            with con.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = 'SELECT * FROM risks WHERE id = %s AND public = 1'
                number = cursor.execute(sql, id)
                if number != 0:
                    risk = cursor.fetchone()
                    sql = 'INSERT INTO risks (name, descript, category, public, user_id) values (%s, %s, %s, 0, %s)'
                number = cursor.execute(sql, (risk["name"], risk["descript"], risk["category"], session["id"]))
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
                        index = 0
                        for risk in risks:
                            sql = "INSERT INTO trows (table_id, risk_id, priority) values (%s, %s, %s)"
                            cursor.execute(sql, (tableId, risk["id"], index))
                            index += 1

                    sql = "SELECT * FROM tables WHERE user_id = %s ORDER BY id DESC  "
                    numberT = cursor.execute(sql, session['id'])
                    tables = cursor.fetchall()
                    con.commit()
                    return render_template('tables/tablesIndex.html', numberT=numberT, tables=tables)
        with con:
            with con.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = "SELECT * FROM tables WHERE user_id = %s ORDER BY id DESC "
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


@app.route("/PAR/tables/edit/down/<int:tid>/<int:rid>", methods=['GET'])
def tablesDown(tid, rid):
    if 'loggedin' in session:
        con = get_con()
        with con:
            with con.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = "SELECT id FROM trows WHERE table_id = %s ORDER BY priority ASC"
                nRows = cursor.execute(sql, tid) - 1
                sql = "SELECT * FROM trows WHERE table_id = %s"
                cursor.execute(sql, tid)
                row = cursor.fetchone()["priority"]
                if row != nRows:
                    print('This is error output', file=sys.stdout)
                    sql = "UPDATE trows SET priority = %s WHERE table_id = %s AND priority = %s"
                    cursor.execute(sql, (row, tid, row + 1))
                    sql = "UPDATE trows SET priority = %s WHERE id = %s"
                    cursor.execute(sql, (row + 1, rid))
                    con.commit()

                return redirect(url_for('.tablesEdit', id=tid))

    return redirect(url_for('.login', msg=5))


@app.route("/PAR/tables/edit/up/<int:tid>/<int:rid>", methods=['GET'])
def tablesUp(tid, rid):
    if 'loggedin' in session:
        con = get_con()
        with con:
            with con.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = "SELECT * FROM trows WHERE table_id = %s"
                cursor.execute(sql, tid)
                row = cursor.fetchone()["priority"]
                if row != 0:
                    sql = "UPDATE trows SET priority = %s WHERE table_id = %s AND priority = %s"
                    cursor.execute(sql, (row, tid, row - 1))
                    sql = "UPDATE trows SET priority = %s WHERE id = %s"
                    cursor.execute(sql, (row - 1, rid))
                    con.commit()

                return redirect(url_for('.tablesEdit', id=tid))

    return redirect(url_for('.login', msg=5))


@app.route("/PAR/tables/edit/<int:id>", methods=['GET', 'POST'])
def tablesEdit(id):
    if 'loggedin' in session:
        prob = ["Lower", "Low", "Moderate", "High", "Higher"]
        imp = ["Negligible", "Low", "Moderate", "High", "Catastrophic"]
        # First Prob Second Impact
        results = {
            "1": {"1": "Low", "2": "Low", "3": "Moderate", "4": "High", "5": "High"},
            "2": {"1": "Low", "2": "Low", "3": "Moderate", "4": "High", "5": "Extreme"},
            "3": {"1": "Low", "2": "Moderate", "3": "High", "4": "Extreme", "5": "Extreme"},
            "4": {"1": "Moderate", "2": "High", "3": "High", "4": "Extreme", "5": "Extreme"},
            "5": {"1": "High", "2": "High", "3": "Extreme", "4": "Extreme", "5": "Extreme"},
        }
        con = get_con()
        with con:
            with con.cursor(pymysql.cursors.DictCursor) as cursor:

                if request.method == "POST":

                    if "type" in request.form:
                        riskid = request.form.get("riskid")
                        sql = "SELECT * FROM risks WHERE id = %s AND user_id = %s"
                        n = cursor.execute(sql, (riskid, session["id"]))
                        if n == 0:
                            sql = "SELECT * FROM risks WHERE id = %s AND public = 1"
                            n = cursor.execute(sql, riskid)
                            scroll = "newRow"

                        if n != 0:
                            risk = cursor.fetchone()
                            sql = "INSERT INTO trows (table_id, risk_id) values (%s, %s)"
                            cursor.execute(sql, (id, risk["id"]))
                            scroll = "newRow"

                    else:
                        probability = request.form.get("prob")
                        impact = request.form.get("impact")
                        solution = request.form.get("solution")
                        rowid = request.form.get("rowid")
                        scroll = f"r{rowid}"
                        result = results[probability][impact]
                        sql = "SELECT * FROM trows WHERE id = %s"
                        cursor.execute(sql, rowid)
                        tid = cursor.fetchone()["table_id"]
                        sql = "SELECT * FROM tables WHERE id = %s "
                        cursor.execute(sql, tid)
                        uid = cursor.fetchone()["user_id"]
                        if uid == session["id"]:
                            if not solution.strip() or solution.strip() == "None":
                                sql = "UPDATE trows SET prob = %s, impact = %s, result = %s, solution = NULL WHERE id = %s"
                                cursor.execute(sql, (probability, impact, result, rowid))
                            else:
                                sql = "UPDATE trows SET prob = %s, impact = %s, result = %s, solution = %s WHERE id = %s"
                                cursor.execute(sql, (probability, impact, result, solution, rowid))

                        else:
                            return redirect(url_for('.login'))

                sql = "SELECT * FROM tables WHERE id = %s"
                cursor.execute(sql, id)
                tname = cursor.fetchone()["name"]
                sql = "SELECT * FROM trows WHERE table_id = %s ORDER BY priority ASC"
                cursor.execute(sql, id)
                trows = cursor.fetchall()
                risks = {}
                for trow in trows:
                    sql = "SELECT * FROM risks WHERE id = %s"
                    cursor.execute(sql, trow["risk_id"])
                    risks[trow["risk_id"]] = cursor.fetchone()

                if request.method == "POST":
                    con.commit()
                    return render_template('tables/tableEdit.html', tname=tname, risks=risks, trows=trows, prob=prob,
                                           imp=imp, scroll=scroll)

        return render_template('tables/tableEdit.html', tname=tname, risks=risks, trows=trows, prob=prob, imp=imp)

    return redirect(url_for('.login', msg=5))


@app.route("/PAR/tables/trow/delete/<int:id>", methods=['GET'])
def trowsDelete(id):
    if 'loggedin' in session:
        con = get_con()
        with con:
            with con.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = 'SELECT * FROM trows WHERE id = %s'
                number = cursor.execute(sql, id)
                tid = cursor.fetchone()["table_id"]
                sql = 'SELECT * FROM tables WHERE id = %s'
                number = cursor.execute(sql, tid)
                uid = cursor.fetchone()["user_id"]
                if uid == session["id"]:
                    sql = 'DELETE FROM trows WHERE id = %s'
                    number = cursor.execute(sql, id)
                    con.commit()

        return redirect(url_for('.tablesEdit', id=tid))

    return redirect(url_for('.login', msg=5))


@app.route("/PAR/search/", methods=['GET'])
def search():
    if 'loggedin' in session:
        con = get_con()
        argss = request.args
        args = argss.to_dict()
        with con:
            with con.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = "SELECT * FROM risks WHERE public = 1 "
                if "auth" in args:
                    auth = "%" + args["auth"] + "%"
                    sqlx = "SELECT * FROM users WHERE username LIKE %s"
                    nu = cursor.execute(sqlx, auth)
                    if nu != 0:
                        aid = cursor.fetchone()["id"]
                        sqlA = f" AND user_id = {aid} "
                        sql = sql + sqlA

                if "cat" in args and args["cat"]:
                    cat = "\'%" + args["cat"] + "%\'"
                    sqlC = f" AND category LIKE {cat} "
                    sql = sql + sqlC

                sql = sql + "ORDER BY id DESC "

                if "number" in args:
                    n = args["number"]
                    sqlN = f" LIMIT {n} "
                    sql = sql + sqlN

                numberR = cursor.execute(sql)
                risks = cursor.fetchall()
                for risk in risks:
                    sqlAut = "SELECT * FROM users WHERE id = %s"
                    cursor.execute(sqlAut, risk["user_id"])
                    risk["auth"] = cursor.fetchone()["username"]

        return render_template('risks/risksSearch.html', risks=risks)

    return redirect(url_for('.login', msg=5))


@app.route("/PAR/tables/pdf/secret/<int:id>/<string:passw>", methods=['GET'])
def pdf(id, passw):
    if passw != 'xlr8':
        return redirect(url_for('.login', msg=5))

    prob = ["Lower", "Low", "Moderate", "High", "Higher"]
    imp = ["Negligible", "Low", "Moderate", "High", "Catastrophic"]
    # First Prob Second Impact
    results = {
        "1": {"1": "Low", "2": "Low", "3": "Moderate", "4": "High", "5": "High"},
        "2": {"1": "Low", "2": "Low", "3": "Moderate", "4": "High", "5": "Extreme"},
        "3": {"1": "Low", "2": "Moderate", "3": "High", "4": "Extreme", "5": "Extreme"},
        "4": {"1": "Moderate", "2": "High", "3": "High", "4": "Extreme", "5": "Extreme"},
        "5": {"1": "High", "2": "High", "3": "Extreme", "4": "Extreme", "5": "Extreme"},
    }
    con = get_con()
    with con:
        with con.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM tables WHERE id = %s"
            cursor.execute(sql, id)
            tname = cursor.fetchone()["name"]
            sql = "SELECT * FROM trows WHERE table_id = %s"
            cursor.execute(sql, id)
            trows = cursor.fetchall()
            risks = {}
            for trow in trows:
                sql = "SELECT * FROM risks WHERE id = %s"
                cursor.execute(sql, trow["risk_id"])
                risks[trow["risk_id"]] = cursor.fetchone()

    return render_template('tables/tablePDF.html', tname=tname, risks=risks, trows=trows, prob=prob,
                           imp=imp)


@app.route("/PAR/tables/pdf/<int:id>", methods=['GET'])
def toPdf(id):
    if 'loggedin' in session:
        url = f"http://127.0.0.1:5000/PAR/tables/pdf/secret/{id}/xlr8"
        pdf = pdfkit.from_url(url, False)
        response = make_response(pdf)

        filename = f"RiskTable{id}.pdf"
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    return redirect(url_for('.login', msg=5))


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

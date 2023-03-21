import requests as requests
from flask import request, url_for, redirect, render_template
from services import login
from app import app


@app.route('/login', methods=['GET', 'POST'])
def login_controller():
    if request.method == 'GET':
        return render_template('auth/login.html')
    else:
        user = login({'email': request.form.get('email'), 'password': request.form.get('password')})

@app.route('/validate', methods=['GET', 'POST'])
def numverify():
    if request.method == 'GET':
        return '''<h1>Please fill out the parameters</h1>
                    <form method="POST" action="/validate">
                    <input type="text" name="acc_key">
                    <input type="text" name="email">
                    <input type="submit" value="Request">
                </form>'''
    else:
        acc_key = request.form['acc_key']
        email = request.form['email']

        req = requests.get('http://apilayer.net/api/check?access_key=' + acc_key + '&email=' + email)
        response = req.json()

        disposable = response["disposable"]
        format_valid = response["format_valid"]
        score = response["score"]
        mx_found = response["mx_found"]

        return redirect(url_for('result', acc_key=acc_key, email=email, format_valid=format_valid,
                                disposable=disposable, score=score, mx_found=mx_found))

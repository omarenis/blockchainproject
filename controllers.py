import json
from typing import Union

import requests as requests
from flask import request, url_for, redirect, render_template, flash
from werkzeug import Response

from models import Person
from services import login, signup
from app import app, login_manager
from flask_login import login_user, login_required


@login_manager.user_loader
def load_user(user_id) -> str:
    return Person.query.get(user_id)


@app.route('/')
def index():
    return 'hello world'


def login_controller() -> Union[Response, str]:
    if request.method == 'POST':
        try:
            user = login({'email': request.form.get('email'), 'password': request.form.get('password')})
            if user:
                login_user(user)
                return redirect('/')
        except Exception as exception:
            flash(str(exception), 'error')
    return render_template('public/login.html')


def signup_controller() -> Union[Response, str]:
    if request.method == 'POST':
        try:
            signup({'email': request.form.get('email'),
                    'firstname': request.form.get('firstname'),
                    'lastname': request.form.get('lastname'),
                    'password': request.form.get('password')
                    })
            return redirect(url_for('login'))
        except Exception as e:
            flash(str(e), 'error')
    return render_template('public/signnup.html')


def upload_file() -> Union[Response, str]:
    if request.method == 'POST':
        json_file = request.files.get('file')
        file_to_save_in_blockhain = str(json.loads(json_file.stream.read()))
        print(file_to_save_in_blockhain)
        return redirect(url_for('upload'))
    return render_template('public/upload_json_file.html')


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

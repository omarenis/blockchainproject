import json
from functools import wraps
from typing import Union
import requests as requests
from flask import request, url_for, redirect, render_template, flash
from werkzeug import Response
from flask.views import MethodView
from app import app, login_manager, session, db
from models import Person
from services import login, verify_code, WorkerService, FileStorageService
from flask_login import login_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, FileField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField(name='username', validators=[DataRequired()])
    password = StringField(name='password', validators=[DataRequired()])


class FileForm(FlaskForm):
    filename = StringField(name='filename')
    fileObject = StringField(name='fileObject')


@login_manager.user_loader
def load_user(user_id) -> str:
    return Person.query.get(user_id)


def admin_required(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if not current_user.is_superuser:
            return login_manager.unauthorized()
        else:
            return f(*args, **kwargs)

    return decorated_func


def login_controller() -> Union[Response, str]:
    if request.method == 'POST':
        try:
            user = login({'email': request.form.get('email'), 'password': request.form.get('password')})
            print(user)
            if user and user.last_login is None:
                return redirect(url_for('verify_code', email=user.email))
            else:
                print(user)
                return redirect(url_for('index'))
        except Exception as exception:
            flash(str(exception), 'error')
    return render_template('public/login.html')


def verify_code_controller():
    if request.method == 'POST':
        verified = verify_code(email=request.form.get('email'), code=request.form.get('code'))
        if verified is True:
            return redirect(url_for('files'))
        else:
            flash('code not verified', 'error')

    return render_template('public/verify_code.html', email=request.args.get('email'))


@login_required
def upload_file() -> Union[Response, str]:
    service = FileStorageService()
    form = FileForm(request.form)
    if request.method == 'POST':
        service.create(form.data, person=current_user)
    return render_template('dashboard/upload_file.html', form=form)


class WorkerCrud(MethodView):
    userService = WorkerService()

    def get(self):
        return render_template("dashboard/worker_crud.html",
                               workers=db.session.execute(db.select(Person).filter_by(is_superuser=False)))

    def post(self):
        if request.form.get('id') is not None:
            person = db.get_or_404(Person, id=request.form.get('id'))
            if person.email != request.form.get('email'):
                person.email = request.form.get('email')
            if person.firstname != request.form.get('firstname'):
                person.firstname = request.form.get('firstname')
            if person.firstname != request.form.get('firstname'):
                person.firstname = request.form.get('firstname')
            if person.lastname != request.form.get('lastname'):
                person.lastname = request.form.get('lastname')
            if request.form.get('password') != '':
                person.set_password(request.data.get('password'))
        else:
            person = Person(email=request.form.get('email'), firstname=request.form.get('firstname'),
                            lastname=request.form.get('lastname'), password=request.form.get('password'))
        db.session.add(person)
        db.session.commit()
        return Response()


def file_view():
    service = FileStorageService()
    form = FileForm()
    if request.method == 'POST':
        service.create(filedata=form.data, person=current_user)
        return 'created !'
    return render_template('dashboard/file_list.html', files=service.list(), form=form)

def worker_create_form():
    return render_template('dashboard/new_worker.html')


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

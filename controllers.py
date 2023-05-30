import json
from functools import wraps
from typing import Union
import requests as requests
from flask import request, url_for, redirect, render_template, flash, jsonify
from werkzeug import Response
from flask.views import MethodView
from app import app, login_manager, session, db
from models import Person, PersonModel
from repositories import OperationRepository
from services import login, verify_code, WorkerService, FileStorageService, CONTRACT
from flask_login import login_user, login_required, current_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, FileField, EmailField, PasswordField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField(name='username', validators=[DataRequired()])
    password = StringField(name='password', validators=[DataRequired()])


class WorkerForm(FlaskForm):
    firstname = StringField(name='firstname', validators=[DataRequired()])
    lastname = StringField(name='lastname', validators=[DataRequired()])
    email = EmailField(name='email', validators=[DataRequired()])
    telephone = EmailField(name='telephone', validators=[DataRequired()])
    location = StringField(name='location', validators=[DataRequired()])
    username = StringField(name='username', validators=[DataRequired()])
    image = StringField(name='image', validators=[DataRequired()])
    password = PasswordField(name='password', validators=[DataRequired()])
    confirm = PasswordField(name='confirm', validators=[DataRequired()])


class FileForm(FlaskForm):
    filename = StringField(name='filename', validators=[DataRequired()])
    file_content = StringField(name='file_content', validators=[DataRequired()])
    file_id = StringField(name='file_id')


@login_manager.user_loader
def load_user(user_id) -> str:
    return PersonModel.query.get(user_id)


def admin_required(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if not current_user.is_superuser:
            return login_manager.unauthorized()
        else:
            return f(*args, **kwargs)

    return decorated_func


def login_controller() -> Union[Response, str]:
    form = LoginForm()
    if request.method == 'POST':
        try:
            user = login({'username': form.data.get('username'), 'password': request.form.get('password')})
            if user and user.is_superuser is False and user.last_login is None:
                return redirect(url_for('verify_code', email=user.email))
            else:
                return redirect(url_for('workers' if user.is_superuser else 'files'))
        except Exception as exception:
            flash(str(exception), 'error')
    return render_template('public/login.html', form=form)


def verify_code_controller():
    if request.method == 'POST':
        verified = verify_code(email=request.form.get('email'), code=request.form.get('code'))
        if verified is True:
            return redirect(url_for('files'))
        else:
            flash('code not verified', 'error')

    return render_template('public/verify_code.html', email=request.args.get('email'))


@login_required
@admin_required
def get_workers():
    service = WorkerService()
    return render_template('dashboard/worker_crud.html', workers=service.list())


@login_required
def worker_form():
    worker_service = WorkerService()
    form = WorkerForm(request.form)
    try:
        worker = worker_service.create(form.data)
        return redirect(url_for('workers' if current_user.is_superuser else 'files'))
    except ValueError as exception:
        flash(str(exception), 'error')
    return render_template('dashboard/new_worker.html')


@login_required
def delete_file():
    file_service = FileStorageService()
    _id = int(request.form.get('id'))
    file_service.delete(_id, current_user)
    return jsonify(message='file deleted'), 200

@login_required
def file_view():
    service = FileStorageService()
    form = FileForm()
    if request.method == 'POST':
        if form.data.get('file_id') is not None:
            service.update({'file_content': form.data.get('file_content'), 'file_id': int(form.data.get('file_id'))},
                           person=current_user)
            flash('file updated successfully', 'success')
        else:
            service.create(filedata=form.data, person=current_user)
            flash('file created successfully', 'success')
    return render_template('dashboard/file_list.html', files=service.list(), form=form)


@login_required
@admin_required
def get_operations():
    operation_repository = OperationRepository(CONTRACT)
    print(current_user.is_superuser)
    return render_template('dashboard/operation_list.html', operations=operation_repository.list())


def worker_create_form():
    worker_service = WorkerService()
    form = WorkerForm()
    if request.method == 'POST':
        worker = worker_service.create(form.data)
    return render_template('dashboard/new_worker.html', form=form)


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


def logout():
    logout_user()
    return redirect(url_for('login'))

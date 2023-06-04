import json
from datetime import timedelta
from functools import wraps
from typing import Union, Tuple
import requests as requests
from flask import request, url_for, redirect, render_template, flash, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt
from werkzeug import Response
from flask_jwt_extended import current_user
from flask_jwt_extended import create_access_token
from app import jwt, db, jwt_redis_blocklist, ACCESS_EXPIRES
from models import PersonModel
from repositories import OperationRepository
from services import login, verify_code, WorkerService, FileStorageService, CONTRACT, send_code

import redis


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return db.session.execute(db.Select(PersonModel).filter_by(id=identity)).scalar_one_or_none()


def login_controller() -> Tuple[Response, int]:
    try:
        user = login({'username': request.json.get('username'), 'password': request.json.get('password')})
        print(user)
        return jsonify(access=create_access_token(identity=user.id)), 200
    except Exception as exception:
        return jsonify(message=str(exception)), 500


def verify_code_controller():
    verified = verify_code(email=request.form.get('email'), code=request.form.get('code'))
    if verified is True:
        return jsonify(message="verified"), 200
    return jsonify(message='not verified'), 403


def send_code_view():
    try:
        send_code(email=request.json.get('email'))
        return jsonify(message="code sent"), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@jwt_required()
def workers():
    service = WorkerService()
    if request.method == 'POST':
        try:
            data = dict(**request.json)
            worker = service.create(data)
            return jsonify(**worker.__dict__), 201
        except ValueError as exception:
            return jsonify(message=str(exception)), 500
    return jsonify([i.__dict__ for i in service.list()])


@jwt_required()
def worker(pk: int):
    worker_service = WorkerService()


@jwt_required()
def files_view():
    service = FileStorageService()
    if request.method == 'POST':
        service.create(request.files['file'], person=current_user)
        return jsonify({'message': 'file created'}), 201
    return jsonify([i.__dict__ for i in service.list()])


@jwt_required()
def file_view(pk: int):
    service = FileStorageService()
    if request.method == 'PUT':
        return jsonify(service.update(_id=pk, file=request.files['file'], person=current_user).__dict__)


@jwt_required()
def get_operations():
    return jsonify([{
        **i.__dict__,
        'person': i.person.__dict__ if current_user.is_superuser is True else None
    } for i in OperationRepository(CONTRACT).list()]), 200


def worker_form(pk: int):
    worker_service = WorkerService()
    if request.method == 'POST':
        return jsonify(worker_service.create(request.json).__dict__), 201
    elif request.method == 'PUT':
        return jsonify(worker_service.update(pk, request.json).__dict__), 200
    else:
        worker_service.delete(pk)
        return jsonify(), 204


@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    jwt_redis_blocklist.set(jti, "", ex=ACCESS_EXPIRES)
    return jsonify(message="Access token revoked")

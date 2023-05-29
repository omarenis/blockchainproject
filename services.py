import json
import random
import string
from datetime import datetime
from flask_login import login_user
from requests import post
from werkzeug.datastructures import FileStorage
from app import db, DOMAIN, CLIENT_ID, CLIENT_SECRET
from models import Person, PersonModel, Contract, File
from contract_interaction import W3, run_get_function
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import hashlib
import base64
from eth_account import Account
import urllib
from uri.uri import URI
from app import app

from repositories import PersonRepository, FileRepository, OperationRepository

with app.app_context():
    CONTRACT = Contract.load_last_uploaded_contract().contract_object

load_dotenv()
FERNET = Fernet(
    base64.b64encode(hashlib.pbkdf2_hmac('sha256', os.environ.get('FERNET_KEY').encode('ascii'),
                                         'hEq52fRbu1WGrU2TIsZ3vtFf7xJp2SMOEC4'.encode('ascii'),
                                         1000))
)


def encode_private_key(private_key_path, passphrase):
    return FERNET.encrypt((Account.from_key(W3.eth.account.decrypt(open(URI(private_key_path).path).read(), passphrase))
                           ).key.hex().encode('utf-8')).decode('utf-8')


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def login(data: dict):
    person = db.session.execute(db.select(PersonModel).filter_by(email=data.get('email'))).scalar_one_or_none()
    print("person = ", type(person))
    if isinstance(person, PersonModel):
        if person.check_password(data.get('password')):
            if person.last_login is None:
                send_code(person.email)
                return person
            else:
                login_user(person)
                person.last_login = datetime.utcnow()
                db.session.commit()
            return person
        raise ValueError('password did not match')
    raise ValueError('person not found with that email')


def send_code(email):
    response = post(f"{DOMAIN}/passwordless/start", data={
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'connection': 'email',
        'send': 'code',
        'email': email
    })
    if response.status_code == 200:
        return json.loads(response.text)
    raise Exception('bad request or invalid code')


def verify_code(email, code):
    response = json.loads(post(f'{DOMAIN}/oauth/token', data={
        "grant_type": "http://auth0.com/oauth/grant-type/passwordless/otp",
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'otp': code,
        'realm': 'email',
        'username': email
    }).text)
    if response.get('access_token') is None:
        raise ValueError(response.get('message'))
    return response


def reset_password(email, action, code=None):
    if action == 'send_code':
        response = post(f"{DOMAIN}/passwordless/start", data={
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'connection': 'email',
            'send': 'code',
            'email': email
        })
        if response.status_code == 200:
            return json.loads(response.text)
    elif action == 'verify_code' and code is not None:
        post(f'{DOMAIN}/oauth/token', data={
            "grant_type": "http://auth0.com/oauth/grant-type/passwordless/otp",
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'otp': code,
        })
    else:
        raise Exception('bad request or invalid code')


class WorkerService(object):

    def __init__(self):
        self.repository = PersonRepository(contract=CONTRACT)

    def create(self, data: dict):
        person = self.repository.contract.functions.getPersonByEmail(data['email']).call()
        if len(person) > 0:
            raise ValueError('person exists with the given email')
        return self.repository.create(data)

    def list(self):
        return self.repository.list()

    def delete(self, _id: int):
        self.repository.delete(_id)


class FileStorageService(object):

    def __init__(self):
        self.contract = CONTRACT
        self.repository = FileRepository(self.contract)
        self.operation_repository = OperationRepository(CONTRACT)

    def list(self):
        files = self.contract.functions.getFiles().call()
        output = []
        for file in files:
            output.append(File(
                _id=file[0],
                filename=file[1],
                file_content=file[2]
            ))
        return output

    def create(self, filedata, person):
        transaction = self.repository.create(filedata)
        self.operation_repository.create({
            'operation': 'create file',
            'filename': filedata['filename'],
            'created_at': datetime.now(),
            'person_id': person.id,
            'transaction_hash': transaction.hex()
        })

    def update(self, filedata, person):
        transaction = self.repository.update(file_content=filedata['file_content'])
        self.operation_repository.create(**{
            'operation': 'update file',
            'filename': filedata['filename'],
            'created_at': datetime.now(),
            'person_id': person.id,
            'transaction_hash': transaction.hash
        })

    def delete(self, _id, person):
        transaction = self.repository.delete(_id=_id)
        self.operation_repository.create(**{
            'operation': 'delete file',
            'created_at': datetime.now(),
            'person_id': person.id,
            'transaction_hash': transaction.hash
        })

import json
import random
import string
from datetime import datetime
from os.path import abspath

from requests import post
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from app import db, DOMAIN, CLIENT_ID, CLIENT_SECRET, client
from models import Person, PersonModel, Contract, File
from contract_interaction import W3, run_get_function
import os
from dotenv import load_dotenv
from app import app

from repositories import PersonRepository, FileRepository, OperationRepository

with app.app_context():
    CONTRACT = Contract.load_last_uploaded_contract().contract_object

load_dotenv()


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def login(data: dict):
    person = db.session.execute(db.select(PersonModel).filter_by(username=data.get('username'))).scalar_one_or_none()
    print(person)
    if isinstance(person, PersonModel):
        if person.check_password(data.get('password')):
            if person.last_login is None and person.is_superuser is False:
                send_code(person.email)
                return person
            else:
                person.last_login = datetime.utcnow()
                db.session.commit()
            return person
        raise ValueError('password did not match')
    raise ValueError('person not found with that username')


def send_code(email):
    run_get_function(CONTRACT.functions.getPersonByEmail, (email, ))
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


def upload_file_to_ipfs(file):
    file.save(secure_filename(file.filename))
    data = client.add(secure_filename(file.filename))
    os.remove(path=abspath(file.filename))
    return data


class WorkerService(object):

    def __init__(self):
        self.repository = PersonRepository(contract=CONTRACT)

    def create(self, data: dict):
        try:
            run_get_function(CONTRACT.functions.getPersonByEmail, (data["email"],))
            raise ValueError('person exists with the given email')
        except ValueError as exception:
            if str(exception).find('not found'):
                person = self.repository.create({
                    'firstname': data['firstname'],
                    'lastname': data['lastname'],
                    'email': data['email'],
                    'telephone': data['telephone'],
                    "location": data['location'],
                    "username": data.get('username'),
                    "password": data.get('password')
                })
                return self.repository.create(data)
            raise exception

    def list(self):
        return self.repository.list()

    def update(self, pk: int, data: dict):
        return self.repository.update(data=data, _id=pk)

    def delete(self, _id: int):
        self.repository.delete(_id)


class FileStorageService(object):

    def save_file(self, file):
        file.save(secure_filename(file.filename))
        file_ipfs_object = client.add(file.filename)
        os.remove(os.path.abspath(file.filename))
        return {
            'filename': file_ipfs_object['Name'],
            'file_content': f'http://127.0.0.1:8080/ipfs/{file_ipfs_object["Hash"]}'
        }

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

    def create(self, file, person):
        filedata = self.save_file(file)
        transaction = self.repository.create(filedata)
        self.operation_repository.create({
            'operation': 'create file',
            'filename': filedata['filename'],
            'created_at': datetime.now(),
            'person_id': person.id,
            'transaction_hash': transaction.hex()
        })

    def update(self, _id: int, file: FileStorage, person):
        filedata = self.save_file(file=file)
        transaction = self.repository.update(file_content=filedata['file_content'], _id=_id)
        self.operation_repository.create({
            'operation': 'update file',
            'filename': filedata['filename'],
            'created_at': datetime.now(),
            'person_id': int(person.id),
            'transaction_hash': transaction.hex()
        })
        return File(_id=_id, file_content=filedata['file_content'], filename=filedata['filename'])

    def delete(self, _id, person):
        transaction = self.repository.delete(_id=_id)
        self.operation_repository.create(**{
            'operation': 'delete file',
            'created_at': datetime.now(),
            'person_id': int(person.get_id()),
            'transaction_hash': transaction.hex()
        })

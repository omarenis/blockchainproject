import json
import random
import string
from datetime import datetime
from flask_login import login_user
from requests import post
from app import db, DOMAIN, CLIEND_ID, CLIENT_SECRET
from models import Person
from contract_interaction import W3

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def login(data: dict):

    person = db.session.execute(db.select(Person).filter_by(email=data.get('email'))).scalar_one_or_none()
    print("person = ", type(person))
    if isinstance(person, Person):
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
        'client_id': CLIEND_ID,
        'client_secret': CLIENT_SECRET,
        'connection': 'email',
        'send': 'code',
        'email': email
    })
    if response.status_code == 200:
        return json.loads(response.text)
    raise Exception('bad request or invalid code')


def signup(data: dict):
    person = Person(email=data.get('email'), password=data.get('password'), firstname=data.get('firstname'),
                    lastname=data.get('lastname'))
    db.session.add(person)
    db.session.commit()
    return "Message sent!"


def verify_code(email, code):
    response = json.loads(post(f'{DOMAIN}/oauth/token', data={
        "grant_type": "http://auth0.com/oauth/grant-type/passwordless/otp",
        'client_id': CLIEND_ID,
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
            'client_id': CLIEND_ID,
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
            'client_id': CLIEND_ID,
            'client_secret': CLIENT_SECRET,
            'otp': code,
        })
    else:
        raise Exception('bad request or invalid code')


class WorkerService(object):

    def __init__(self, contract_address, abi):
        self.contract = W3.eth.contract(address=contract_address, abi=abi)

    def create(self, data: dict):
        person  = self.contract.functions.getPersonByEmail(data['email'])
        if person:
            raise ValueError('email can not be used for this worker')

        account = W3.eth.account.create(data['email'])
        address = account.address
        private_key = address.privateKey

        person = Person()
        acount = W3.eth.account.create(data.get('email'))


class FileStorageService(object):

    def __init__(self, contract_address):
        self.contract_address = contract_address

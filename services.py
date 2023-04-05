import json
import random
import string

from models import Person
from requests import get, post
from email_validator import validate_email, EmailNotValidError
from app import db, Message, mail, DOMAIN, CLIEND_ID, CLIENT_SECRET
from flask_login import login_user

HEADERS = {
    'apikey': 'fUbsfKbIAYCI11NpOsug0mpuZ4FJjALb'
}


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def validate(email):
    if validate_email(email):
        response = get(f"https://api.apilayer.com/email_verification/check?email={email}", headers=HEADERS)
        if response.json()['smtp_check'] is False:
            raise EmailNotValidError("the email does not support smtp")


def login(data: dict):
    validate(data.get('email'))
    person = db.first_or_404(Person, email=data.get('email'))
    if isinstance(person, Person):
        if person.check_password(data.get('password')):
            login_user(person)
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
    validate(data.get('email'))
    person = Person(email=data.get('email'), password=data.get('password'), firstname=data.get('firstname'),
                    lastname=data.get('lastname'))
    db.session.add(person)
    db.session.commit()
    print(person)
    print(send_code(person.email))
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

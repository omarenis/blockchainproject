import random
import string

from models import Person
from requests import get
from email_validator import validate_email, EmailNotValidError
from app import db, Message, mail

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


def signup(data: dict):
    validate(data.get('email'))
    data['password'] = get_random_string(12)
    person = Person(**data)
    db.session.add(person)
    db.session.commit()
    msg = Message(f"Hello sir with email! {data.get('email')}\nyour new password is {data.get('password')}",
                  recipients=[data.get('email')])
    mail.send(msg)
    return "Message sent!"

from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash
from app import db, UserMixin


class Person(db.Model, UserMixin):

    __tablename__ = 'persons'

    email = db.Column(db.String, unique=True, nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String())
    is_superuser = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime(), default=None, nullable=True)

    def __init__(self, email, firstname, lastname, password, *args, **kwargs):
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.set_password(password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password) -> bool:
        return check_password_hash(self.password, password)

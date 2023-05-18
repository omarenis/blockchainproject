import json
from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash
from app import db, UserMixin
from contract_interaction import submit_transaction_hash, W3


class Person(db.Model, UserMixin):
    __tablename__ = 'persons'

    address = db.Column(db.String, unique=True, nullable=False)
    id = db.Column(db.Integer, primary_key=True)
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


class Contract(db.Model):
    __tablename__ = 'contracts'
    W3 = W3
    contract_address = db.Column(db.String(255), primary_key=True)
    abi = db.Column(db.Text, nullable=False)
    bytecode = db.Column(db.Text, nullable=False)

    def __init__(self, contact_address, abi, bytecode=None):
        self.contract_address = contact_address
        self.abi = abi
        self.bytecode = bytecode
        self.contract = W3.eth.contract(address=contact_address, abi=abi, bytecode=bytecode)
        self.coinbase = W3.eth.coinbase

    @classmethod
    def deploy(cls, abi, bytecode):
        contract = cls.W3.eth.contract(abi=abi, bytecode=bytecode).constructor()
        authenticated = cls.W3.geth.personal.unlock_account(cls.W3.eth.coinbase, '11608168')
        if authenticated:
            tx = contract.transact({
                'from': cls.W3.eth.coinbase,
                'nonce': cls.W3.eth.get_transaction_count(cls.W3.eth.coinbase),
                'gas': 2000000
            })

            tx_receipt = submit_transaction_hash(tx)
            if tx_receipt is not None and tx_receipt.contractAddress is not None:
                contract = cls(contact_address=tx_receipt.contractAddress, abi=json.dumps(abi), bytecode=bytecode)
                db.session.add(contract)
                db.session.commit()
                return contract
        else:
            return Exception("not authenticated")

import json
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from app import db, UserMixin
from contract_interaction import submit_transaction_hash, W3
from sqlalchemy import ForeignKey, Column, String, Text, Integer, Boolean, DateTime
from sqlalchemy import String

class PersonModel(db.Model, UserMixin):
    __tablename__ = 'persons'

    address = Column(String, unique=True, nullable=False)
    private_key = Column(Text, nullable=False)
    id = Column(Integer, primary_key=True)
    password = Column(String())
    is_superuser = Column(Boolean, default=False)
    last_login = Column(DateTime(), default=None, nullable=True)
    operations = db.Relationship('Operation', backref='person', lazy=True)

    def __init__(self, address, private_key, password=None, is_superuser=False, *args, **kwargs):
        self.address = address
        self.private_key = private_key
        self.is_superuser = is_superuser

    def check_password(self, password) -> bool:
        return check_password_hash(self.password, password)

    def set_password(self, password):
        self.password = generate_password_hash(password)


class ContractModel(db.Model):
    __tablename__ = 'contracts'
    W3 = W3
    contract_address = Column(String(255), primary_key=True)
    abi = Column(Text, nullable=False)
    bytecode = Column(Text, nullable=False)

    def __init__(self, contract_address, abi, bytecode=None):
        self.contract_address = contract_address
        self.abi = abi
        self.bytecode = bytecode
        self.coinbase = W3.eth.coinbase

    def load_contract(self):
        return W3.eth.contract(address=self.contract_address, abi=json.loads(self.abi), bytecode=self.bytecode)

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
            print(tx_receipt)
            if tx_receipt is not None and tx_receipt.contractAddress is not None:
                print(tx_receipt.keys())
                contract = cls(contract_address=tx_receipt.contractAddress, abi=json.dumps(abi), bytecode=bytecode)
                db.session.add(contract)
                db.session.commit()
                return contract
        else:
            return Exception("not authenticated")


class OperationModel(db.Model):
    __tablename__ = 'operations'
    id = Column(Integer, primary_key=True)
    person = Column(Integer, db.ForeignKey('persons.id'))
    transaction_hash = Column(Text, nullable=False)
    created_at = Column(DateTime())


class Person(object):

    def __init__(self, email, firstname, lastname, location, telephone, image, private_key, password=None):
        self.password = password
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.private_key = private_key
        self.location = location
        self.telephone = telephone
        self.image = image


class File(object):

    def __init__(self, filename, file_content):
        self.filename = filename
        self.file_content = file_content


class Operation(object):
    def __init__(self, person: Person, file: File, transaction_hash):
        self.person = person
        self.file = file
        self.transaction_hash = transaction_hash

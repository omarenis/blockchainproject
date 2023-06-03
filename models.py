import json
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from contract_interaction import submit_transaction_hash, W3, compile_source_file
from sqlalchemy import ForeignKey, Column, String, Text, Integer, Boolean, DateTime
from sqlalchemy import String


def get_results(data):
    return [i[0] for i in data]


class PersonModel(db.Model):
    __tablename__ = 'persons'

    id = Column(Integer, primary_key=True)
    password = Column(String())
    username = Column(String, )
    is_superuser = Column(Boolean, default=False)
    last_login = Column(DateTime(), default=None, nullable=True)
    operations = db.Relationship('OperationModel', backref='person', lazy=True)

    def __init__(self, is_superuser=False, password=None, *args, **kwargs):
        self.is_superuser = is_superuser
        if password is not None:
            self.set_password(password)

    def check_password(self, password) -> bool:
        return check_password_hash(self.password, password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    @classmethod
    def create_admin_account(cls):
        admin = cls()
        admin.is_superuser = True
        admin.username = 'admin'
        admin.set_password(password='admin@admin')
        db.session.add(admin)
        db.session.commit()


class ContractModel(db.Model):
    __tablename__ = 'contracts'
    W3 = W3
    contract_address = Column(String(255), primary_key=True)
    abi = Column(Text, nullable=False)

    def __init__(self, abi, contract_address, *args, **kwargs):
        self.abi = abi
        self.contract_address = contract_address

    def load_contract(self):
        return W3.eth.contract(address=self.contract_address, abi=json.loads(self.abi), bytecode=self.bytecode)


class OperationModel(db.Model):
    __tablename__ = 'operations'
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, db.ForeignKey('persons.id'))
    operation = Column(Text, nullable=False)
    transaction_hash = Column(Text, nullable=False)
    filename = Column(Text, nullable=False)
    created_at = Column(DateTime())


class Person(object):

    def __init__(self, _id, username, email, firstname, lastname, location, telephone, password=None):
        self.id = _id
        self.username = username
        self.password = password
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.location = location
        self.telephone = telephone


def load_last_contract():
    data = db.session.execute(db.Select(ContractModel)).all()[-1][0]
    return W3.eth.contract(address=data.contract_address, abi=json.loads(data.abi))


class Contract(object):
    coinbase = W3.eth.accounts[0]

    def __init__(self, abi, contract_address=None, bin=None):
        self.abi = abi
        if contract_address is None and bin is None:
            raise ValueError('contract address or binj must not be null')
        self.contract_address = contract_address
        self.bin = bin
        self.contract_object = W3.eth.contract(address=contract_address, abi=abi, bytecode=bin)

    @classmethod
    def load_last_uploaded_contract(cls):
        contract = db.session.execute(db.Select(ContractModel)).first()
        if contract is None:
            Contract.deploy()
        contract_instance = db.session.execute(db.Select(ContractModel)).first()[0]
        return Contract(abi=contract_instance.abi, contract_address=contract_instance.contract_address)

    @classmethod
    def deploy(cls):
        db.drop_all()
        db.create_all()
        contract_compilation = compile_source_file()
        contract = W3.eth.contract(abi=contract_compilation['abi'], bytecode=contract_compilation['bin']).constructor()
        print(W3.eth.accounts[0])
        authenticated = W3.geth.personal.unlock_account(cls.coinbase, '')
        if authenticated:
            tx = contract.transact({
                'from': cls.coinbase,
                'nonce': W3.eth.get_transaction_count(cls.coinbase),
                'gas': contract.estimate_gas()
            })
            tx_receipt = submit_transaction_hash(tx)
            if tx_receipt is not None and tx_receipt.contractAddress is not None and tx_receipt.status == 1:
                print(tx_receipt.contractAddress)
                contract = ContractModel(contract_address=tx_receipt.contractAddress,
                                         abi=json.dumps(contract_compilation['abi']))
                db.session.add(contract)
                db.session.commit()
                return contract
        else:
            return Exception("not authenticated")


class File(object):

    def __init__(self, _id, filename, file_content):
        self.id = _id
        self.filename = filename
        self.file_content = file_content


class Operation(object):
    def __init__(self, _id: int, person: Person, filename: str, transaction_hash, created_at):
        self.id = _id
        self.person = person
        self.filename = filename
        self.transaction_hash = transaction_hash
        self.created_at  = created_at

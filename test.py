import time
from app import app, db
from contract_interaction import W3, compile_source_file, submit_transaction_hash, execute_set_function
from models import ContractModel, Person, Contract
from web3.middleware import simple_cache_middleware

from repositories import FileRepository

W3.middleware_onion.add(simple_cache_middleware)


def test_deploy():
    with app.app_context():
        Contract.deploy()


def test_create_person():
    with app.app_context():
        contract = Contract.load_last_uploaded_contract().contract_object
        transaction = contract.functions.createPerson(2, 'firstname', 'lastname', 'email', 'telephone', 'location',
                                                      'image')
        W3.geth.personal.unlock_account(W3.eth.accounts[0], '')
        print(transaction.transact({
            'from': W3.eth.accounts[0],
            'gas': transaction.estimate_gas(),
            'nonce': W3.eth.get_transaction_count(W3.eth.accounts[0])
        }))


def test_get_persons():
    with app.app_context():
        contract = Contract.load_last_uploaded_contract().contract_object
        fileRepository = FileRepository(contract)
        fileRepository.get_files()
        data = dict()
        print(contract.functions.getPersons().call())
        data['id'], data['firstname'], data['lastname'], data['email'], data['telephone'], data['location'], data[
            'image'] = contract.functions.getPersonById(2).call()


def test_create_file():
    with app.app_context():
        W3.geth.personal.unlock_account(W3.eth.accounts[0], '')
        contract = Contract.load_last_uploaded_contract().contract_object
        execute_set_function(contract.functions.addFile, ('filename', 'fileObject'), W3.eth.accounts[0])



def test_get_files():
    with app.app_context():
        contract = Contract.load_last_uploaded_contract().contract_object
        print(contract.functions.getFiles().call())

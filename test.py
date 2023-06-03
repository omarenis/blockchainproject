import json
import time
from app import app, db
from contract_interaction import W3, compile_source_file, submit_transaction_hash, execute_set_function
from models import ContractModel, Person, Contract, PersonModel
from web3.middleware import simple_cache_middleware

from repositories import FileRepository, OperationRepository
from services import FileStorageService, WorkerService, CONTRACT

W3.middleware_onion.add(simple_cache_middleware)


def test_deploy():
    with app.app_context():
        Contract.deploy()


def test_get_person_by_id():
    with app.app_context():
        result = db.session.execute(db.Select(PersonModel).filter_by(id=6)).scalar_one_or_none()
        print(result)


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


def test_crate_worker():
    with app.app_context():
        workerService = WorkerService()
        worker = workerService.create({
            'firstname': 'test',
            'lastname': 'test',
            'email': 'test@test.com',
            'telephone': '+21624127616',
            'location': 'test location',
            'image': 'image',
            'password': 'password'
        })
        print(worker.__dict__)


def test_list_workers():
    with app.app_context():
        workerService = WorkerService()
        print(workerService.list())


def test_create_file():
    with app.app_context():
        service = FileStorageService()
        file = service.create({'filename': 'filename', 'file_content': 'file_content'},
                              db.session.execute(db.Select(PersonModel).filter_by(id=6)).scalar_one())


def test_get_files():
    with app.app_context():
        try:
            contract = Contract.load_last_uploaded_contract().contract_object
            print(contract.functions.getPersonById(1).call())
        except ValueError as exception:
            data = eval(str(exception))
            message = data.get('message')
            print(message[message.find('revert') + len('revert'):])


def test_get_file_by_id():
    contract = Contract.load_last_uploaded_contract().contract_object
    print(contract.functions.get)


def test_get_operations():
    with app.app_context():
        operation_repository = OperationRepository(CONTRACT)
        print(operation_repository.list())

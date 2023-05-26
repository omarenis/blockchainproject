import time
from app import app, db
from contract_interaction import W3, compile_source_file, submit_transaction_hash
from models import ContractModel, Person, Contract
from web3.middleware import simple_cache_middleware

W3.middleware_onion.add(simple_cache_middleware)

with app.app_context():
    contract = Contract.load_last_uploaded_contract().contract_object
    print(contract.functions.createPerson(2, 'firstname', 'lastname', 'email', 'telephone', 'location', 'image'))

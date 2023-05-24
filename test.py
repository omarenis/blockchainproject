import time
from app import app, db
from contract_interaction import W3
from models import ContractModel, Person
from contract_interaction import ABI, BYTECODE
from web3.middleware import simple_cache_middleware
W3.middleware_onion.add(simple_cache_middleware)
with app.app_context():
    db.drop_all()
    db.create_all()
    ContractModel.deploy(abi=ABI, bytecode=BYTECODE)
    # print(W3.eth.syncing)
    # contract = db.session.execute(db.Select(Contract)).first()[0].load_contract()
    # print(contract.functions.getPersons().call())

#     contract = db.session.execute(db.Select(Contract)).first()[0].load_contract()
#     print(contract)
#
#
# print(contract.functions.getPersons().transact({
#
# }))

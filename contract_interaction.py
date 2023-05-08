import base64
import hashlib
import json
import os
from time import sleep
from datetime import date
from os.path import dirname
import pandas as pd
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from web3 import Web3
from werkzeug.security import generate_password_hash

load_dotenv()

CONTRACT_CSV_FILEPATH = dirname(__file__) + '/contracts.csv'
FILEPATH = dirname(__file__) + '/accounts.csv'
IPC_FILE = '/home/trikiomar/nodes/node1/geth.ipc'
W3 = Web3(Web3.IPCProvider(IPC_FILE))
COINTBASE = W3.eth.coinbase
ABI = json.loads(open('./contract-abi.txt').read().replace('\n', '').replace('\t', ''))
BYTECODE = open('./contract-bin.txt', 'r').read().replace('\n', '')
FERNET = Fernet(
    base64.b64encode(hashlib.pbkdf2_hmac('sha256', os.environ.get('FERNET_KEY').encode('ascii'),
                                         'hEq52fRbu1WGrU2TIsZ3vtFf7xJp2SMOEC4'.encode('ascii'),
                                         1000))
)


def submit_transaction_hash(transaction_hash):
    W3.geth.miner.start(1)
    while True:
        try:
            tx_receipt = W3.eth.wait_for_transaction_receipt(transaction_hash)
            sleep(10)
            if tx_receipt is not None:
                W3.geth.miner.stop()
                return tx_receipt
        except Exception as exception:
            print(exception, end="")


def deploy_contract():
    contract = W3.eth.contract(abi=ABI, bytecode=BYTECODE).constructor()
    gas_price = contract.estimateGas()
    authenticated = W3.geth.personal.unlock_account(COINTBASE, '11608168')
    if authenticated:
        tx = contract.transact({
            'from': W3.eth.coinbase,
            'nonce': W3.eth.get_transaction_count(COINTBASE),
            'gasPrice': gas_price
        })
        W3.geth.miner.start(1)
        tx_receipt = submit_transaction_hash(tx)
        if tx_receipt is not None and tx_receipt.contractAddress is not None:
            dataframe = pd.read_csv(CONTRACT_CSV_FILEPATH, sep=";")
            dataframe = dataframe.append(
                {
                    'contractAddress': tx_receipt.contractAddress,
                    'dateDeployment': date.today()
                },
                ignore_index=True
            )
            dataframe.to_csv(CONTRACT_CSV_FILEPATH, sep=";", index=False)
            return tx_receipt.contractAddress
    else:
        return Exception("not authenticated")

class FileStorageService():
    
    def __init__(contract_address):
        self.contact_address = contract_address
    
    def save():
        pass
    
    def delete():
        pass
    
    def retreive(_id: int):
        pass
    
    def put(_id: int, data: dict):
        pass
    
    def create(data: dict):
        pass
 

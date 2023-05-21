import base64
import hashlib
import json
import os
from time import sleep
from datetime import date
from os.path import dirname
from web3 import Web3
from solcx import compile_source

CONTRACT_CSV_FILEPATH = dirname(__file__) + '/contracts.csv'
FILEPATH = dirname(__file__) + '/accounts.csv'
W3 = Web3(Web3.IPCProvider('/home/ubuntu/ethereum_database/data/geth.ipc'))
private_key = None
# try:
#     COINTBASE = W3.eth.coinbase
# except Exception as exception:
#     account = W3.eth.account.create('11608168')
#     W3.miner.set_etherebase(account.address)
#     COINTBASE = account.address
#     private_key = account.privateKey


dir_path = os.path.dirname(os.path.realpath(__file__))
ABI = json.loads(open(f'{dir_path}/contract-abi.txt').read().replace("\n", ""))
BYTECODE = open(f'{dir_path}/contract-bin.txt', 'r').read().replace("\n", "")


def compile_source_file():
    with open(f"{dir_path}/smartcontract.sol", "r") as f:
        return compile_source(f.read(), output_values=['abi', 'bin']).popitem()[1]


def submit_transaction_hash(transaction_hash):
    while True:
        try:
            tx_receipt = W3.eth.wait_for_transaction_receipt(transaction_hash)
            sleep(10)
            if tx_receipt is not None and tx_receipt.contractAddress is not None:
                return tx_receipt
        except Exception as exception:
            print(exception, end="")

import base64
import hashlib
import json
import os
from time import sleep
from datetime import date
from os.path import dirname
from web3 import Web3
from solcx import compile_source
from solcx import install_solc

CONTRACT_CSV_FILEPATH = dirname(__file__) + '/contracts.csv'
FILEPATH = dirname(__file__) + '/accounts.csv'
W3 = Web3(Web3.HTTPProvider('http://localhost:9545'))
private_key = None
install_solc('latest')

dir_path = os.path.dirname(os.path.realpath(__file__))
ACCOUNT = W3.eth.accounts[0]


def compile_source_file():
    with open(f"{dir_path}/smartcontract.sol", "r") as f:
        return compile_source(f.read(), output_values=['abi', 'bin']).popitem()[1]


def submit_transaction_hash(transaction_hash):
    while True:
        try:
            tx_receipt = W3.eth.wait_for_transaction_receipt(transaction_hash)
            print(tx_receipt)
            if tx_receipt is not None and tx_receipt.contractAddress is not None:
                return tx_receipt
        except Exception as exception:
            print(exception, end="")


def create_account(passphrase):
    account = W3.geth.personal.new_account(passphrase)
    if W3.eth.get_balance(account) <= 10000000000:
        W3.geth.miner.set_etherbase(account)
        W3.geth.miner.start()
        while W3.eth.get_balance(account) <= 10000000000:
            sleep(5)
            if W3.eth.get_balance(account) >= 10000000000:
                W3.geth.miner.stop()
                W3.geth.miner.set_etherbase(ACCOUNT)
                return {
                    'account': account,
                    'wallet': W3.geth.personal.list_wallets()[-1]
                }


def run_get_function(function, params=None):
    try:
        transaction = function() if params is None else function(*params)
        return transaction.call()
    except Exception as exception:
        data = eval(str(exception))
        message = data.get('message')
        raise ValueError(message[message.find('revert') + len('revert'):])


def execute_set_function(function, params, address):
    W3.geth.personal.unlock_account(address, '')
    transaction = function(*params)
    return transaction.transact({
        'from': address,
        'nonce': W3.eth.get_transaction_count(address),
        'gas': transaction.estimate_gas()
    })

from eth_account import Account
import urllib
from uri.uri import URI
from contract_interaction import compile_source_file, W3
from app import app, db

list_wallets = W3.geth.personal.list_wallets()
for wallet in list_wallets:
    print((Account.from_key(W3.eth.account.decrypt(open(URI(wallet.accounts[0].url).path).read(), '11608168'))).key)


file = URI("keystore:///home/ubuntu/ethereum_database/data/keystore/UTC--2023-05-18T19-27-03.109794285Z--bf7408b915e9b03ce82316d5c6d26575871928d1").path

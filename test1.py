from web3 import Web3
alchemy_url = "https://eth-sepolia.g.alchemy.com/v2/Tshrkx71i-5z5KCET_U_3JF0346IOAjq"
w3 = Web3(Web3.HTTPProvider(alchemy_url))
print(w3.is_connected())

# Get the latest block number
latest_block = w3.eth.block_number
print(latest_block)

# Get the balance of an account
balance = w3.eth.get_balance('0x742d35Cc6634C0532925a3b844Bc454e4438f44e')

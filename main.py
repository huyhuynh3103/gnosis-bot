from web3 import Web3
from dotenv import load_dotenv
import os
from web3.middleware import geth_poa_middleware
from gnosis.eth import EthereumClient
from gnosis.eth.contracts import get_erc721_contract
from gnosis.safe import Safe

load_dotenv()
api_key = os.getenv("API_KEY")


RPC_URL = "https://saigon-archive.roninchain.com/rpc?apikey="+api_key
TOKEN_ADDRESS = "0x5448955aF1FC5C6c5e19b0Ab177E5D3a28268Fee"
SAFE_ADDRESS = ""

def main():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    ethereum_client = EthereumClient(RPC_URL)
    erc721_contract = get_erc721_contract(ethereum_client.w3, TOKEN_ADDRESS)
    # safe = Safe(SAFE_ADDRESS, ethereum_client)

    name, symbol = ethereum_client.batch_call([
        erc721_contract.functions.name(),
        erc721_contract.functions.symbol(),
    ])

    print(name, symbol)
    print(w3.eth.get_block('latest'))

if __name__ == '__main__':
    main()
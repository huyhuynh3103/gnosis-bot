from web3 import Web3
from dotenv import load_dotenv
import os
from web3.middleware import geth_poa_middleware
from gnosis.eth import EthereumClient
from gnosis.safe import Safe

load_dotenv()
api_key = os.getenv("API_KEY")
rpc_url = os.getenv("TESTNET_URL")
private_key = os.getenv("PRIVATE_KEY")
# rpc_url = os.getenv("MAINNET_URL")

RPC_URL = rpc_url + "?apikey=" + api_key
SAFE_ADDRESS = "0x31B18347BADe159DBBa6D4de92247947233BC060"  # testnet
STAKING_PROXY = "0x9C245671791834daf3885533D24dce516B763B28"  # testnet
VALIDATOR = "0xAcf8Bf98D1632e602d0B1761771049aF21dd6597"  # testnet
STAKING_ABI = '[{"inputs":[{"internalType":"address","name":"_consensusAddr","type":"address"}],"name":"delegate","outputs":[],"stateMutability":"payable","type":"function"}]'

w3 = Web3(Web3.HTTPProvider(RPC_URL))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
ethereum_client = EthereumClient(RPC_URL)
safe = Safe(SAFE_ADDRESS, ethereum_client)
staking_proxy = w3.eth.contract(address=STAKING_PROXY, abi=STAKING_ABI)
OPERATION_CALL = 0
OPERATION_DELEGATE_CALL = 1


def main():
    safe_info = safe.retrieve_all_info()
    print("safe_info: ", safe_info)
    data = staking_proxy.encodeABI(fn_name='delegate', args=[VALIDATOR])
    print("delegate info: ", data)
    gas = safe.estimate_tx_gas(to=STAKING_PROXY, value=10, data=data, operation=OPERATION_DELEGATE_CALL)
    print("estimate gas: ", gas)
    safe_tx = safe.build_multisig_tx(to=STAKING_PROXY, value=10, data=data, safe_tx_gas=gas)
    print("safe_tx: ", safe_tx)
    # owner 1 sign
    safe_tx.sign(private_key)
    is_success = safe_tx.call() == 1
    print("check safe_tx ok: ", is_success)
    print(w3.eth.get_block('latest'))
    safe_tx.execute(private_key)


if __name__ == '__main__':
    main()

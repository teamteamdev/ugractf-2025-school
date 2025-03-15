from itertools import batched
from kyzylborda_lib.secrets import get_flag
from web3 import Web3


RPC_URL = "https://ethereum-holesky-rpc.publicnode.com"
DEPLOYER_ADDRESS = "0x4A78C96E051967988b5D6548D438c14d49310A9a"
PRIVATE_KEY = "<REDACTED>"

MASK = bytes.fromhex('d087f450a472071dad29898d9a036e7a755f80efa5f7146e1785f509e0741ecd')
KEY = [7, 8, 11, 4, 12, 3, 9, 2, 13, 15, 6, 10, 14, 0, 5, 1]

BASE_BYTECODE = "61016e8061000c5f395ff3fe7fd087f450a472071dad29898d9a036e7a755f80efa5f7146e1785f509e0741ecd7fa2f59729c51c6842df50ece3e3731b1d073eed8ad1984b0d67f1865683017dbf8161004d604435610098565b189161005a606435610098565b189103610094577f91c6b511d41a687adf50c8ccdb4231141a2bf28ee4b64b0d67f18c56a1355f8c036100905760015f5260205ff35b5f80fd5b5f80fd5b8060701c9069ffff000000000000000061ffff60e01b8260e01b1661ffff60a01b8360901b161761ffff60f01b8360d01b161763ffff00008360201c16176bffff000000000000000000008360101b161761ffff60901b8360401b161761ffff8360601c161765ffff000000008360501c161761ffff60d01b8360501b16176dffff0000000000000000000000008360301c161761ffff60c01b8360201b161767ffff0000000000008360801c161761ffff60b01b8360101c16179160901c161761ffff60701b8216179061ffff60801b16179056"

def encryptBlock(block):
    perm = [None] * 16
    for i, x in enumerate(batched(block, 2)):
        perm[KEY[i]] = "".join(x)

    permBlock = bytearray("".join(perm).encode())
    for i in range(len(permBlock)):
        permBlock[i] ^= MASK[i]

    return bytes(permBlock)

w3 = Web3(Web3.HTTPProvider(RPC_URL))
CHAIN_ID = w3.eth.chain_id

def generate():
    lastBlock = encryptBlock(get_flag()[32:]).hex()
    bytecode = BASE_BYTECODE.replace("91c6b511d41a687adf50c8ccdb4231141a2bf28ee4b64b0d67f18c56a1355f8c", lastBlock)
    
    contract = w3.eth.contract(abi=[], bytecode=bytecode)

    nonce = w3.eth.get_transaction_count(DEPLOYER_ADDRESS)
    transaction = contract.constructor().build_transaction({
        "chainId": CHAIN_ID,
        "from": DEPLOYER_ADDRESS,
        "nonce": nonce
    })
    signed_tx = w3.eth.account.sign_transaction(transaction, private_key=PRIVATE_KEY)
    sent_tx = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    reciept = w3.eth.wait_for_transaction_receipt(sent_tx)
    deployedContract = reciept.contractAddress

    return {
        "urls": [
            f"https://holesky.etherscan.io/address/{deployedContract}"
        ]
    }


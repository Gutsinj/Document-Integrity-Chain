from crypto.hash_utils import sha256
from storage.ipfs_client import add_file
from blockchain.merkle_tree import MerkleTree
from blockchain.block import Block
from crypto.signer import sign_block
import time

def prepare_block(file_paths, prev_hash, index, signer_id, private_key):
    merkle_tree = MerkleTree(hash_files(file_paths))

    block = Block(
        index=index,
        timestamp=time.time(),
        prev_hash=prev_hash,
        signer_id=signer_id,
        merkle_root=merkle_tree,
        signature=sign_block(block, private_key),
    )


def hash_file(file_path):
    with open(file_path, 'rb') as f:
        file_data = f.read()
        return sha256(file_data)
    

def hash_files(file_paths):
    return [hash_file(file_path) for file_path in file_paths]
from crypto.hash_utils import sha256
from storage.ipfs_client import add_file
from blockchain.merkle_tree import MerkleTree
from blockchain.block import Block
from crypto.signer import sign_block
import time

# Prepare a block for the blockchain
def prepare_block(file_paths, prev_hash, index, signer_id, private_key):
    merkle_tree = MerkleTree(hash_files(file_paths))

    block = Block(
        index=index,
        timestamp=time.time(),
        merkle_tree=merkle_tree,
        prev_hash=prev_hash,
        signer_id=signer_id,
        private_key=private_key,
    )

    return block

# Hash a file
def hash_file(file_path):
    with open(file_path, 'rb') as f:
        file_data = f.read()
        return sha256(file_data)
    
# Hash a list of files
def hash_files(file_paths):
    return [hash_file(file_path) for file_path in file_paths]
from blockchain.block import Block
import time
from crypto.key_manager import get_public_key_from_id

class Blockchain:
    # Initialize empty blockchain with genesis block
    def __init__(self):
        self.chain = []
        self.create_starting_block()

    # Create and add the first block (genesis block)
    def create_starting_block(self):
        start = Block(0, time.time(), 0, 0, 0)
        self.chain.append(start)

    # Return the most recent block in the chain
    def get_latest_block(self):
        return self.chain[-1]

    # Add a new block after validation
    def add_block(self, block):
        if self.get_latest_block().compute_hash() != block.prev_hash:
            return False
        
        pub_key = get_public_key_from_id(block.signer_id)
        if not block.verify_block_signature(pub_key):
            return False

        if block.compute_hash() != block.hash:
            return False
        
        self.chain.append(block)
        return True
        
    # Validate the integrity of a blockchain
    def is_valid_chain(self, chain):
        if not chain or len(chain) == 0:
            return False
        
        prev = 0
        for i in range(len(chain)):
            block = chain[i]
            
            pub_key = get_public_key_from_id(block.signer_id)
            if not block.verify_block_signature(pub_key):
                return False

            if block.prev_hash != prev or block.compute_hash() != block.hash:
                return False
            prev = chain[i].compute_hash()
        
        return True

    # Replace current chain with longest valid chain from peers
    def resolve_forks(self, peerChains):
        longest_found = self.chain
        max_length = len(self.chain)

        for chain in peerChains:
            if self.is_valid_chain(chain) and len(chain) > max_length:
                longest_found = chain
                max_length = len(chain)

        if max_length > len(self.chain):
            self.chain = longest_found
            return True
        else:
            return False
import json
from crypto.hash_utils import sha256
from crypto.signer import sign_digest, verify_signature

class Block:
    # Initialize block with data and compute hash
    def __init__(self, index, timestamp, merkle_tree, prev_hash, signer_id, private_key):
        self.index = index
        self.timestamp = timestamp
        self.merkle_tree = merkle_tree  # Store the complete merkle tree
        self.merkle_root = merkle_tree.root  # Keep root for backward compatibility
        self.prev_hash = prev_hash
        self.signer_id = signer_id
        self.signature = None
        self.sign_block(private_key)
        self.hash = self.compute_hash()
    
    # Generate SHA256 hash from block data
    def compute_hash(self):
        data = {
            'index': self.index,
            'timestamp': self.timestamp,
            'merkle_root': self.merkle_root.hex() if isinstance(self.merkle_root, bytes) else self.merkle_root,
            'prev_hash': self.prev_hash.hex() if isinstance(self.prev_hash, bytes) else self.prev_hash,
            'signer_id': self.signer_id,
            'signature': self.signature.hex() if isinstance(self.signature, bytes) else self.signature
        }
        data_serialized = json.dumps(data)
        return sha256(data_serialized)
    
    # Generates the signature from the partial header data
    def sign_block(self, private_key):
        data = {
            'index': self.index,
            'timestamp': self.timestamp,
            'merkle_root': self.merkle_root.hex() if isinstance(self.merkle_root, bytes) else self.merkle_root,
            'prev_hash': self.prev_hash.hex() if isinstance(self.prev_hash, bytes) else self.prev_hash,
            'signer_id': self.signer_id
        }
        data_serialized = json.dumps(data)
        header_digest = sha256(data_serialized)

        self.signature = sign_digest(header_digest, private_key)

    def verify_block_signature(self, public_key):
        header_digest = self.compute_hash()
        data = {
            'index': self.index,
            'timestamp': self.timestamp,
            'merkle_root': self.merkle_root.hex() if isinstance(self.merkle_root, bytes) else self.merkle_root,
            'prev_hash': self.prev_hash.hex() if isinstance(self.prev_hash, bytes) else self.prev_hash,
            'signer_id': self.signer_id
        }
        data_serialized = json.dumps(data)
        header_digest = sha256(data_serialized)
        return verify_signature(header_digest, self.signature, public_key)

    # Verify if a file hash exists in the block's merkle tree
    def verify_file_in_block(self, file_hash):
        return self.merkle_tree.verify(file_hash)

    # Get the merkle proof for a file hash in the block's merkle tree
    def get_file_proof(self, file_hash):
        try:
            return self.merkle_tree.generate_proof(file_hash, self.merkle_tree.leaves)
        except ValueError:
            return None
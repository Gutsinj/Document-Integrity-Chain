import json
from crypto.hash_utils import sha256

class Block:
    def __init__(self, index, timestamp, merkle_root, prev_hash):
        self.index = index
        self.timestamp = timestamp
        self.merkle_root = merkle_root
        self.prev_hash = prev_hash

        self.hash = self.computeHash()
    
    def computeHash(self):
        data = {
            'index': self.index,
            'timestamp': self.timestamp,
            'merkle_root': self.merkle_root,
            'prev_hash': self.prev_hash
        }
        data_serialized = json.dumps(data)
        return sha256(data_serialized)
    
# m = Block(1, 5, 6, 8)
# print(m.computeHash())
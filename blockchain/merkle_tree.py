from crypto.hash_utils import sha256

LEFT = 'left'
RIGHT = 'right'

class MerkleTree():
    # Initialize Merkle tree with leaf hashes
    def __init__(self, hashes):
        self.leaves = hashes
        self.tree = None
        self.root = None

        self.generate_merkle_tree(hashes)

    # Determine if a leaf hash is positioned left or right
    def get_leaf_direction(self, hash):
        hash_index = self.tree[0].index(hash)
        
        if hash_index % 2 == 0:
            return LEFT
        else:
            return RIGHT
    
    # Duplicate last hash if odd number of hashes
    def make_even(self, hashes):
        if len(hashes) % 2 != 0:
            hashes.append(hashes[-1])

    # Recursively build tree levels by pairing and hashing
    def generate_tree(self, hashes, tree):
            if len(hashes) == 1:
                return hashes
            
            self.make_even(hashes)
            combined = []

            for i in range(0, len(hashes), 2):
                concat_hashes = hashes[i] + hashes[i + 1]
                combined.append(sha256(concat_hashes))

            tree.append(combined)
            return self.generate_tree(combined, tree)

    # Generate complete Merkle tree and set root
    def generate_merkle_tree(self, hashes):
        if not hashes or len(hashes) == 0:
            return None

        tree = [hashes]
        self.generate_tree(hashes, tree)
        self.tree = tree
        self.root = tree[-1][0]
    
    # Generate proof path for a specific hash
    def generate_proof(self, hash, hashes):
        if not hash or not hashes or len(hashes) == 0:
            return None
        
        tree = self.tree
        merkle_proof = [{'hash': hash, 'direction': self.get_leaf_direction(hash)}]
        hash_index = tree[0].index(hash)

        for level in range(len(tree) - 1):
            is_left = hash_index % 2 == 0
            sibling_direction = None
            sibling_index = None
            if is_left:
                sibling_direction = RIGHT
                sibling_index = hash_index + 1
            else:
                sibling_direction = LEFT
                sibling_index = hash_index - 1

            merkle_proof.append({'hash': tree[level][sibling_index], 'direction': sibling_direction})
            hash_index = hash_index // 2
        
        return merkle_proof

    # Calculate root hash from Merkle proof
    def get_root_from_merkle_proof(self, merkle_proof):
        if not merkle_proof or len(merkle_proof) == 0:
            return None
        
        current = merkle_proof[0]
        for proof in merkle_proof[1:]:
            if proof['direction'] == RIGHT:
                combined = current['hash'] + proof['hash']
            else:
                combined = proof['hash'] + current['hash']
            current = {'hash': sha256(combined)}
        
        return current['hash']
    
    # Verify if hash exists in tree using proof verification
    def verify(self, hash, root=None):
        if not root: 
            root = self.root
        
        try:
            proof = self.generate_proof(hash, self.leaves)
            return root == self.get_root_from_merkle_proof(proof)
        except ValueError:
            return False
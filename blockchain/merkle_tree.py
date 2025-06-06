from crypto.hash_utils import sha256

LEFT = 'left'
RIGHT = 'right'

class MerkleTree():
    # Initialize Merkle tree with leaf hashes
    def __init__(self, hashes):
        self.leaves = hashes
        self.tree = None
        self.root = None

        self.generateMerkleTree(hashes)

    # Determine if a leaf hash is positioned left or right
    def getLeafDirection(self, hash):
        hashIndex = self.tree[0].index(hash)
        
        if hashIndex % 2 == 0:
            return LEFT
        else:
            return RIGHT
    
    # Duplicate last hash if odd number of hashes
    def makeEven(self, hashes):
        if len(hashes) % 2 != 0:
            hashes.append(hashes[-1])

    # Recursively build tree levels by pairing and hashing
    def generateTree(self, hashes, tree):
            if len(hashes) == 1:
                return hashes
            
            self.makeEven(hashes)
            combined = []

            for i in range(0, len(hashes), 2):
                concatHashes = hashes[i] + hashes[i + 1]
                combined.append(sha256(concatHashes))

            tree.append(combined)
            return self.generateTree(combined, tree)

    # Generate complete Merkle tree and set root
    def generateMerkleTree(self, hashes):
        if not hashes or len(hashes) == 0:
            return None

        tree = [hashes]
        self.generateTree(hashes, tree)
        self.tree = tree
        self.root = tree[-1][0]
    
    # Generate proof path for a specific hash
    def generateProof(self, hash, hashes):
        if not hash or not hashes or len(hashes) == 0:
            return None
        
        tree = self.tree
        merkleProof = [{'hash': hash, 'direction': self.getLeafDirection(hash)}]
        hashIndex = tree[0].index(hash)

        for level in range(len(tree) - 1):
            isLeft = hashIndex % 2 == 0
            siblingDirection = None
            siblingIndex = None
            if isLeft:
                siblingDirection = RIGHT
                siblingIndex = hashIndex + 1
            else:
                siblingDirection = LEFT
                siblingIndex = hashIndex - 1

            merkleProof.append({'hash': tree[level][siblingIndex], 'direction': siblingDirection})
            hashIndex = hashIndex // 2
        
        return merkleProof

    # Calculate root hash from Merkle proof
    def getRootFromMerkleProof(self, merkleProof):
        if not merkleProof or len(merkleProof) == 0:
            return None
        
        current = merkleProof[0]
        for proof in merkleProof[1:]:
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
            proof = self.generateProof(hash, self.leaves)
            return root == self.getRootFromMerkleProof(proof)
        except ValueError:
            return False
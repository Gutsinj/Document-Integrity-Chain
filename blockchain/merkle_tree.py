from crypto.hash_utils import sha256
import math

LEFT = 'left'
RIGHT = 'right'

class MerkleTree():
    def __init__(self, hashes):
        self.leaves = hashes
        self.tree = None
        self.root = None

        self.generateMerkleTree(hashes)

    def getLeafDirection(self, hash):
        hashIndex = self.tree[0].index(hash)
        
        if hashIndex % 2 == 0:
            return LEFT
        else:
            return RIGHT
    
    def makeEven(self, hashes):
        if len(hashes) % 2 != 0:
            hashes.append(hashes[-1])

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

    def generateMerkleTree(self, hashes):
        if not hashes or len(hashes) == 0:
            return None

        tree = [hashes]
        self.generateTree(hashes, tree)
        self.tree = tree
        self.root = tree[-1][0]
    
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
    
    def verify(self, hash):
        try:
            proof = self.generateProof(hash, self.leaves)
            return self.root == self.getRootFromMerkleProof(proof)
        except ValueError:
            return False
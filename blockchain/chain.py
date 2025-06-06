from blockchain.block import Block
import time

class Blockchain:
    # Initialize empty blockchain with genesis block
    def __init__(self):
        self.chain = []
        self.createStartingBlock()

    # Create and add the first block (genesis block)
    def createStartingBlock(self):
        start = Block(0, time.time(), 0, 0)
        self.chain.append(start)

    # Return the most recent block in the chain
    def getLatestBlock(self):
        return self.chain[-1]

    # Add a new block after validation
    def addBlock(self, block):
        if self.getLatestBlock().computeHash() != block.prev_hash:
            return False
        
        if block.computeHash() != block.hash:
            return False
        
        self.chain.append(block)
        return True
        
    # Validate the integrity of a blockchain
    def isValidChain(self, chain):
        if not chain or len(chain) == 0:
            return False
        
        prev = 0
        for i in range(len(chain)):
            block = chain[i]
            if block.prev_hash != prev or block.computeHash() != block.hash:
                return False
            prev = chain[i].computeHash()
        
        return True

    # Replace current chain with longest valid chain from peers
    def resolve_forks(self, peerChains):
        longest_found = self.chain
        max_length = len(self.chain)

        for chain in peerChains:
            if self.isValidChain(chain) and len(chain) > max_length:
                longest_found = chain
                max_length = len(chain) 

        if max_length > len(self.chain):
            self.chain = longest_found
            return True
        else:
            return False
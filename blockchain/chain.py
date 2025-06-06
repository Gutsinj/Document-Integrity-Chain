from block import Block
from datetime import datetime

class Blockchain:
    def __init__(self):
        self.chain = []
        self.createStartingBlock()

    def createStartingBlock(self):
        start = Block(0, datetime.now(), 0, 0)
        self.chain.append(start)

    def getLatestBlock(self):
        return self.chain[-1]

    def addBlock(self, block):
        if self.getLatestBlock().computeHash() != block.prev_hash:
            return False
        
        if block.computeHash() != block.hash:
            return False
        
        self.chain.append(block)
        return True
        
    def validateChain(self):
        pass

    def resolve_forks(self):
        pass
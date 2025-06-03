import datetime

class Block:
    INDEX = 0

    def __init__(self):
        self.index = Block.INDEX
        self.timestamp = datetime.time()
        self.prev_hash = None
        self.doc_hash = None
        self.merkle_root = None

        Block.INDEX += 1

    def get_block(self):
        pass
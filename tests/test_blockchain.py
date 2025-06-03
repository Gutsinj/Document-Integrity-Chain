from blockchain.block import Block

def check_index_incrementation():
    b1 = Block()
    assert(b1.index == 0)
    b2 = Block()
    assert(b2.index == 1)
    assert(Block.INDEX == 2)

check_index_incrementation()
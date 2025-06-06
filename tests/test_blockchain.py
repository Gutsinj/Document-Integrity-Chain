import time
import json
import unittest
from blockchain.block import Block
from blockchain.chain import Blockchain
from crypto.hash_utils import sha256
from blockchain.merkle_tree import MerkleTree, LEFT, RIGHT


class TestMerkleTree(unittest.TestCase):
    def setUp(self):
        self.leaf_a = sha256("a")
        self.leaf_b = sha256("b")
        self.leaf_c = sha256("c")
        self.leaves = [self.leaf_a, self.leaf_b, self.leaf_c]
        self.mt = MerkleTree(self.leaves.copy())

    def test_tree_structure_and_levels(self):
        tree = self.mt.tree
        # After duplication: [a, b, c, c]
        self.assertEqual(len(tree), 3)
        self.assertEqual(len(tree[0]), 4)
        self.assertEqual(tree[0], [self.leaf_a, self.leaf_b, self.leaf_c, self.leaf_c])

        # Level 1: parent hashes
        expected_parent_0 = sha256(self.leaf_a + self.leaf_b)
        expected_parent_1 = sha256(self.leaf_c + self.leaf_c)
        self.assertEqual(tree[1], [expected_parent_0, expected_parent_1])

        # Level 2: root
        expected_root = sha256(expected_parent_0 + expected_parent_1)
        self.assertEqual(tree[2], [expected_root])

    def test_root_property(self):
        level0 = [self.leaf_a, self.leaf_b, self.leaf_c, self.leaf_c]
        parent0 = sha256(level0[0] + level0[1])
        parent1 = sha256(level0[2] + level0[3])
        expected = sha256(parent0 + parent1)
        self.assertEqual(self.mt.root, expected)

    def test_get_leaf_direction(self):
        self.assertEqual(self.mt.getLeafDirection(self.leaf_a), LEFT)
        self.assertEqual(self.mt.getLeafDirection(self.leaf_b), RIGHT)
        self.assertEqual(self.mt.getLeafDirection(self.leaf_c), LEFT)

    def test_generate_and_validate_proof(self):
        for leaf in [self.leaf_a, self.leaf_b, self.leaf_c]:
            proof = self.mt.generateProof(leaf, self.leaves)
            self.assertIsInstance(proof, list)
            self.assertGreater(len(proof), 0)
            self.assertEqual(proof[0]["hash"], leaf)

            reconstructed = self.mt.getRootFromMerkleProof(proof)
            self.assertEqual(reconstructed, self.mt.root)
            self.assertTrue(self.mt.verify(leaf))

        bogus = sha256("not-in-tree")
        self.assertFalse(self.mt.verify(bogus))

    def test_generate_proof_sibling_order(self):
        proof_c = self.mt.generateProof(self.leaf_c, self.leaves)
        self.assertEqual(proof_c[0]["hash"], self.leaf_c)
        self.assertEqual(proof_c[0]["direction"], LEFT)
        self.assertEqual(proof_c[1]["hash"], self.leaf_c)
        self.assertEqual(proof_c[1]["direction"], RIGHT)

        parent_ab = sha256(self.leaf_a + self.leaf_b)
        self.assertEqual(proof_c[2]["hash"], parent_ab)
        self.assertEqual(proof_c[2]["direction"], LEFT)

    def test_make_even_odd_leaves(self):
        temp = ["x", "y", "z"]
        mt_temp = MerkleTree(["x", "y", "z"])
        mt_temp.makeEven(temp)
        self.assertEqual(len(temp), 4)
        self.assertEqual(temp[-1], "z")

    def test_generate_tree_empty(self):
        mt_empty = MerkleTree([])
        self.assertIsNone(mt_empty.tree)
        self.assertIsNone(mt_empty.root)

    def test_verify_raises_false_on_missing_leaf(self):
        missing = sha256("missing")
        self.assertFalse(self.mt.verify(missing))


class TestBlock(unittest.TestCase):
    def setUp(self):
        self.test_index = 1
        self.test_timestamp = time.time()
        self.test_merkle_root = "abc123"
        self.test_prev_hash = "def456"
        self.block = Block(self.test_index, self.test_timestamp, self.test_merkle_root, self.test_prev_hash)

    def test_block_initialization(self):
        # Block properties are set correctly
        self.assertEqual(self.block.index, self.test_index)
        self.assertEqual(self.block.timestamp, self.test_timestamp)
        self.assertEqual(self.block.merkle_root, self.test_merkle_root)
        self.assertEqual(self.block.prev_hash, self.test_prev_hash)
        self.assertIsNotNone(self.block.hash)

    def test_compute_hash_consistency(self):
        # Hash should be deterministic - same inputs produce same hash
        hash1 = self.block.computeHash()
        hash2 = self.block.computeHash()
        self.assertEqual(hash1, hash2)
        self.assertEqual(hash1, self.block.hash)

    def test_compute_hash_different_data(self):
        # Different block data should produce different hashes
        block2 = Block(2, self.test_timestamp, self.test_merkle_root, self.test_prev_hash)
        self.assertNotEqual(self.block.hash, block2.hash)

    def test_hash_matches_manual_computation(self):
        # Verify hash computation matches expected SHA256 result
        expected_data = {
            'index': self.test_index,
            'timestamp': self.test_timestamp,  # Now using timestamp float
            'merkle_root': self.test_merkle_root,
            'prev_hash': self.test_prev_hash
        }
        expected_serialized = json.dumps(expected_data)
        expected_hash = sha256(expected_serialized)
        self.assertEqual(self.block.hash, expected_hash)

    def test_genesis_block(self):
        # Genesis block with zero values
        genesis = Block(0, 0, 0, 0)  # Use 0 for timestamp instead of datetime
        self.assertEqual(genesis.index, 0)
        self.assertEqual(genesis.timestamp, 0)
        self.assertEqual(genesis.merkle_root, 0)
        self.assertEqual(genesis.prev_hash, 0)
        self.assertIsNotNone(genesis.hash)


class TestBlockchain(unittest.TestCase):
    def setUp(self):
        self.blockchain = Blockchain()

    def test_blockchain_initialization(self):
        # Blockchain should start with genesis block
        self.assertEqual(len(self.blockchain.chain), 1)
        genesis = self.blockchain.chain[0]
        self.assertEqual(genesis.index, 0)
        self.assertEqual(genesis.merkle_root, 0)
        self.assertEqual(genesis.prev_hash, 0)
        self.assertIsNotNone(genesis.hash)

    def test_add_valid_block(self):
        # Adding a valid block should succeed
        latest = self.blockchain.getLatestBlock()
        new_block = Block(1, time.time(), "merkle123", latest.computeHash())
        
        result = self.blockchain.addBlock(new_block)
        self.assertTrue(result)
        self.assertEqual(len(self.blockchain.chain), 2)
        self.assertEqual(self.blockchain.getLatestBlock(), new_block)

    def test_add_invalid_block(self):
        # Adding block with wrong prev_hash should fail
        invalid_block = Block(1, time.time(), "merkle123", "wrong_hash")
        
        result = self.blockchain.addBlock(invalid_block)
        self.assertFalse(result)
        self.assertEqual(len(self.blockchain.chain), 1)

    def test_is_valid_chain(self):
        # Valid chain should return True
        self.assertTrue(self.blockchain.isValidChain(self.blockchain.chain))
        
        # Add valid block and test again
        latest = self.blockchain.getLatestBlock()
        new_block = Block(1, time.time(), "merkle123", latest.computeHash())
        self.blockchain.addBlock(new_block)
        self.assertTrue(self.blockchain.isValidChain(self.blockchain.chain))
        
        # Empty chain should return False
        self.assertFalse(self.blockchain.isValidChain([]))
        self.assertFalse(self.blockchain.isValidChain(None))

    def test_resolve_forks(self):
        # Create longer valid chain
        longer_chain = [self.blockchain.chain[0]]  # Start with same genesis
        prev_hash = longer_chain[0].computeHash()
        
        for i in range(1, 3):  # Add 2 more blocks
            block = Block(i, time.time(), f"merkle{i}", prev_hash)
            longer_chain.append(block)
            prev_hash = block.computeHash()
        
        # Should replace current chain with longer one
        result = self.blockchain.resolve_forks([longer_chain])
        self.assertTrue(result)
        self.assertEqual(len(self.blockchain.chain), 3)
        
        # Shorter chain should not replace current chain
        shorter_chain = [self.blockchain.chain[0]]
        result = self.blockchain.resolve_forks([shorter_chain])
        self.assertFalse(result)
        self.assertEqual(len(self.blockchain.chain), 3)

if __name__ == "__main__":
    unittest.main()
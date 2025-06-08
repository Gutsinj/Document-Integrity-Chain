import time
import json
import unittest
import os
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
        self.assertEqual(self.mt.get_leaf_direction(self.leaf_a), LEFT)
        self.assertEqual(self.mt.get_leaf_direction(self.leaf_b), RIGHT)
        self.assertEqual(self.mt.get_leaf_direction(self.leaf_c), LEFT)

    def test_generate_and_validate_proof(self):
        for leaf in [self.leaf_a, self.leaf_b, self.leaf_c]:
            proof = self.mt.generate_proof(leaf, self.leaves)
            self.assertIsInstance(proof, list)
            self.assertGreater(len(proof), 0)
            self.assertEqual(proof[0]["hash"], leaf)

            reconstructed = self.mt.get_root_from_merkle_proof(proof)
            self.assertEqual(reconstructed, self.mt.root)
            self.assertTrue(self.mt.verify(leaf))

        bogus = sha256("not-in-tree")
        self.assertFalse(self.mt.verify(bogus))

    def test_generate_proof_sibling_order(self):
        proof_c = self.mt.generate_proof(self.leaf_c, self.leaves)
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
        mt_temp.make_even(temp)
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
        # generate test keypair for signing
        from crypto.key_manager import generate_keypair, load_private_key, load_public_key
        self.signer_id = "test"
        self.test_output_path = './tests/keys'
        os.makedirs(self.test_output_path, exist_ok=True)
        
        # Backup existing key_registry.json if it exists
        self.registry_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "key_registry.json")
        if os.path.exists(self.registry_path):
            with open(self.registry_path, 'r') as f:
                self.original_registry = json.load(f)
        else:
            self.original_registry = {}
            
        generate_keypair(output_path=self.test_output_path, signer_id=self.signer_id)
        self.priv_key = load_private_key('./tests/keys/private_key_test.pem')
        self.pub_key = load_public_key('./tests/keys/public_key_test.pem')

        self.test_index = 1
        self.test_timestamp = time.time()
        self.test_merkle_root = "abc123"
        self.test_prev_hash = "def456"
        # include private key in block creation
        self.block = Block(self.test_index, self.test_timestamp, self.test_merkle_root, self.test_prev_hash, self.signer_id, self.priv_key)

    def tearDown(self):
        # Restore original key_registry.json
        with open(self.registry_path, 'w') as f:
            json.dump(self.original_registry, f, indent=4)
        # Clean up test keys
        for key_file in os.listdir(self.test_output_path):
            if (key_file.startswith("private_key_") or key_file.startswith("public_key_")) and \
               (key_file.endswith("genesis.pem") or key_file.endswith("test.pem")):
                os.remove(os.path.join(self.test_output_path, key_file))

    def test_block_initialization(self):
        # Block properties are set correctly
        self.assertEqual(self.block.index, self.test_index)
        self.assertEqual(self.block.timestamp, self.test_timestamp)
        self.assertEqual(self.block.merkle_root, self.test_merkle_root)
        self.assertEqual(self.block.prev_hash, self.test_prev_hash)
        self.assertIsNotNone(self.block.hash)
        # signature fields should be set after init
        self.assertIsNotNone(self.block.signature)
        self.assertIsNotNone(self.block.signer_id)

    def test_compute_hash_consistency(self):
        # Hash should be deterministic - same inputs produce same hash
        hash1 = self.block.compute_hash()
        hash2 = self.block.compute_hash()
        self.assertEqual(hash1, hash2)
        self.assertEqual(hash1, self.block.hash)

    def test_compute_hash_different_data(self):
        # Different block data should produce different hashes
        block2 = Block(2, self.test_timestamp, self.test_merkle_root, self.test_prev_hash, self.signer_id, self.priv_key)
        self.assertNotEqual(self.block.hash, block2.hash)

    def test_hash_matches_manual_computation(self):
        # Verify hash computation matches expected SHA256 result
        expected_data = {
            'index': self.test_index,
            'timestamp': self.test_timestamp,
            'merkle_root': self.test_merkle_root.hex() if isinstance(self.test_merkle_root, bytes) else self.test_merkle_root,
            'prev_hash': self.test_prev_hash.hex() if isinstance(self.test_prev_hash, bytes) else self.test_prev_hash,
            'signer_id': self.block.signer_id,
            'signature': self.block.signature.hex() if isinstance(self.block.signature, bytes) else self.block.signature
        }
        expected_serialized = json.dumps(expected_data)
        expected_hash = sha256(expected_serialized)
        self.assertEqual(self.block.hash, expected_hash)

    def test_sign_and_verify(self):
        # Verify that block.verify_block_signature works
        self.assertTrue(self.block.verify_block_signature(self.pub_key))

    def test_genesis_block(self):
        # Genesis block with zero values and no signing key
        genesis = Block(0, 0, 0, 0, 0, self.priv_key)
        self.assertEqual(genesis.index, 0)
        self.assertEqual(genesis.timestamp, 0)
        self.assertEqual(genesis.merkle_root, 0)
        self.assertEqual(genesis.prev_hash, 0)
        self.assertIsNotNone(genesis.hash)
        self.assertIsNotNone(genesis.signer_id)


class TestBlockchain(unittest.TestCase):
    def setUp(self):
        from crypto.key_manager import generate_keypair, get_private_key_from_id, get_public_key_from_id
        # setup blockchain and test keypair
        self.signer_id = 'test'
        self.test_output_path = './tests/keys'
        self.main_keys_path = './keys'
        os.makedirs(self.test_output_path, exist_ok=True)
        os.makedirs(self.main_keys_path, exist_ok=True)
        
        # Backup existing key_registry.json if it exists
        self.registry_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "key_registry.json")
        if os.path.exists(self.registry_path):
            with open(self.registry_path, 'r') as f:
                self.original_registry = json.load(f)
        else:
            self.original_registry = {}
            
        generate_keypair(output_path=self.test_output_path, signer_id=self.signer_id)
        self.blockchain = Blockchain()
        self.priv_key = get_private_key_from_id(self.signer_id)
        self.pub_key = get_public_key_from_id(self.signer_id)

    def tearDown(self):
        # Restore original key_registry.json
        with open(self.registry_path, 'w') as f:
            json.dump(self.original_registry, f, indent=4)
            
        # Clean up test keys in both directories
        for directory in [self.test_output_path, self.main_keys_path]:
            if os.path.exists(directory):
                for key_file in os.listdir(directory):
                    if (key_file.startswith("private_key_") or key_file.startswith("public_key_")) and \
                       (key_file.endswith("genesis.pem") or key_file.endswith("test.pem")):
                        os.remove(os.path.join(directory, key_file))

    def test_blockchain_initialization(self):
        # Blockchain should start with genesis block
        self.assertEqual(len(self.blockchain.chain), 1)
        genesis = self.blockchain.chain[0]
        self.assertEqual(genesis.index, 0)
        self.assertEqual(genesis.merkle_root, 0)
        self.assertEqual(genesis.prev_hash, 0)
        self.assertIsNotNone(genesis.hash)
        self.assertIsNotNone(genesis.signature)
        self.assertIsNotNone(genesis.signer_id)

    def test_add_valid_block(self):
        latest = self.blockchain.get_latest_block()
        # include private key in block creation
        new_block = Block(1, time.time(), "merkle123", latest.compute_hash(), self.signer_id, self.priv_key)

        result = self.blockchain.add_block(new_block)
        self.assertTrue(result)
        self.assertEqual(len(self.blockchain.chain), 2)
        self.assertEqual(self.blockchain.get_latest_block(), new_block)

    def test_add_invalid_block(self):
        invalid_block = Block(1, time.time(), "merkle123", "wrong_hash", self.signer_id, self.priv_key)
        
        result = self.blockchain.add_block(invalid_block)
        self.assertFalse(result)
        self.assertEqual(len(self.blockchain.chain), 1)

    def test_is_valid_chain(self):
        # Valid chain should return True
        self.assertTrue(self.blockchain.is_valid_chain(self.blockchain.chain))

        # Add valid block and test again
        latest = self.blockchain.get_latest_block()
        new_block = Block(1, time.time(), "merkle123", latest.compute_hash(), self.signer_id, self.priv_key)
        self.blockchain.add_block(new_block)
        self.assertTrue(self.blockchain.is_valid_chain(self.blockchain.chain))

        # Empty or None chain should return False
        self.assertFalse(self.blockchain.is_valid_chain([]))
        self.assertFalse(self.blockchain.is_valid_chain(None))

    def test_resolve_forks(self):
        # Create longer valid chain
        longer_chain = [self.blockchain.chain[0]]
        prev_hash = longer_chain[0].compute_hash()

        for i in range(1, 3):
            block = Block(i, time.time(), f"merkle{i}", prev_hash, self.signer_id, self.priv_key)
            longer_chain.append(block)
            prev_hash = block.compute_hash()

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
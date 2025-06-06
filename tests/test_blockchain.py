import unittest
from blockchain.block import Block
from crypto.hash_utils import sha256
from blockchain.merkle_tree import MerkleTree, LEFT, RIGHT


class TestMerkleTree(unittest.TestCase):
    def set_up(self):
        # Create three sample leaves by hashing simple strings.
        # sha256 in hash_utils will encode str to bytes automatically.
        self.leaf_a = sha256("a")
        self.leaf_b = sha256("b")
        self.leaf_c = sha256("c")
        self.leaves = [self.leaf_a, self.leaf_b, self.leaf_c]
        self.mt = MerkleTree(self.leaves.copy())

    def test_tree_structure_and_levels(self):
        """
        For three leaves, the tree should duplicate the last leaf ("c") to make an even count.
        Level 0 (leaves): length 4 after duplication
        Level 1 (parents of pairs): length 2
        Level 2 (root): length 1
        """
        tree = self.mt.tree
        # After duplication: [a, b, c, c]
        self.assertEqual(len(tree), 3)                        # Three levels: leaves, parents, root
        self.assertEqual(len(tree[0]), 4)                     # 3 original + 1 duplicate
        self.assertEqual(tree[0], [self.leaf_a, self.leaf_b, self.leaf_c, self.leaf_c])

        # Level 1: parent hashes of pairs (a‖b) and (c‖c)
        expected_parent_0 = sha256(self.leaf_a + self.leaf_b)
        expected_parent_1 = sha256(self.leaf_c + self.leaf_c)
        self.assertEqual(len(tree[1]), 2)
        self.assertEqual(tree[1][0], expected_parent_0)
        self.assertEqual(tree[1][1], expected_parent_1)

        # Level 2: single root hash = sha256(parent_0‖parent_1)
        expected_root = sha256(expected_parent_0 + expected_parent_1)
        self.assertEqual(len(tree[2]), 1)
        self.assertEqual(tree[2][0], expected_root)

    def test_root_property(self):
        """ The .root property should match the single hash at the top of tree. """
        computed_root = self.mt.root
        # Recompute expected root directly
        level0 = [self.leaf_a, self.leaf_b, self.leaf_c, self.leaf_c]
        parent0 = sha256(level0[0] + level0[1])
        parent1 = sha256(level0[2] + level0[3])
        expected = sha256(parent0 + parent1)
        self.assertEqual(computed_root, expected)

    def test_get_leaf_direction(self):
        """
        getLeafDirection should return LEFT for even indices, RIGHT for odd.
        After duplication: indices are [0:a, 1:b, 2:c, 3:c]
        """
        tree0 = self.mt.tree[0]
        # index of leaf_a = 0 → LEFT
        self.assertEqual(self.mt.getLeafDirection(self.leaf_a), LEFT)
        # index of leaf_b = 1 → RIGHT
        self.assertEqual(self.mt.getLeafDirection(self.leaf_b), RIGHT)
        # index of leaf_c = 2 (first occurrence) → LEFT
        self.assertEqual(self.mt.getLeafDirection(self.leaf_c), LEFT)

    def test_generate_and_validate_proof(self):
        """
        For each original leaf, generateProof + getRootFromMerkleProof should reconstruct the root.
        Also, verify() should return True for valid leaves and False for an invalid hash.
        """
        for leaf in [self.leaf_a, self.leaf_b, self.leaf_c]:
            proof = self.mt.generateProof(leaf, self.leaves)
            # Proof should be a non-empty list of dicts
            self.assertIsInstance(proof, list)
            self.assertGreater(len(proof), 0)
            # The first element must reference the leaf itself
            self.assertEqual(proof[0]["hash"], leaf)

            # Reconstruct root from proof
            reconstructed = self.mt.getRootFromMerkleProof(proof)
            self.assertEqual(reconstructed, self.mt.root)

            # verify() should return True for that leaf
            self.assertTrue(self.mt.verify(leaf))

        # An entirely bogus hash should fail verification
        bogus = sha256("not-in-tree")
        self.assertFalse(self.mt.verify(bogus))

    def test_generate_proof_sibling_order(self):
        """
        Confirm that the sibling order in the proof matches LEFT/RIGHT logic.
        Specifically for leaf_c (index 2):
          - At level 0: index 2 is even → LEFT, sibling is index 3 (c) with direction RIGHT.
          - At level 1: after pairing, index 2//2 = 1 at level1, which is odd → RIGHT, sibling index 0 with direction LEFT.
        """
        proof_c = self.mt.generateProof(self.leaf_c, self.leaves)
        # Proof structure: [ {hash:c, direction:LEFT}, {hash:sibling_c, direction:RIGHT}, {hash: parent_ab, direction:LEFT} ]
        self.assertEqual(proof_c[0]["hash"], self.leaf_c)
        self.assertEqual(proof_c[0]["direction"], LEFT)

        # Next sibling at level0 is the duplicated c
        self.assertEqual(proof_c[1]["hash"], self.leaf_c)
        self.assertEqual(proof_c[1]["direction"], RIGHT)

        # Parent-level sibling is hash(ab)
        parent_ab = sha256(self.leaf_a + self.leaf_b)
        self.assertEqual(proof_c[2]["hash"], parent_ab)
        self.assertEqual(proof_c[2]["direction"], LEFT)

    def test_make_even_odd_leaves(self):
        """
        If the user supplies an odd number of leaves directly to makeEven, the last leaf should be duplicated.
        We'll bypass generateMerkleTree and call makeEven explicitly.
        """
        temp = ["x", "y", "z"]  # treat as placeholders (strings)
        mt_temp = MerkleTree(["x", "y", "z"])  # we only need makeEven, tree isn't used here
        mt_temp.makeEven(temp)
        self.assertEqual(len(temp), 4)
        self.assertEqual(temp[-1], "z")  # last element must be duplicated

    def test_generate_tree_empty(self):
        """ If generateMerkleTree is given an empty list, it should return None. """
        mt_empty = MerkleTree([])
        self.assertIsNone(mt_empty.tree)
        self.assertIsNone(mt_empty.root)

    def test_verify_raises_false_on_missing_leaf(self):
        """
        If generateProof is called on a leaf not in the tree, a ValueError
        would be raised when .index() is called, and verify() should catch it and return False.
        """
        # Choose some arbitrary string not in self.leaves
        missing = sha256("missing")
        # Directly call verify to ensure it returns False, not an exception
        self.assertFalse(self.mt.verify(missing))

if __name__ == "__main__":
    unittest.main()

# def check_index_incrementation():
#     b1 = Block()
#     assert(b1.index == 0)
#     b2 = Block()
#     assert(b2.index == 1)
#     assert(Block.INDEX == 2)



# if __name__ == "__main__":
#     check_index_incrementation()

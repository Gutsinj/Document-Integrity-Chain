import unittest
import os
import json
from crypto.hash_utils import sha256
from crypto.key_manager import (
    generate_keypair,
    load_private_key,
    load_public_key,
    get_public_key_from_id,
    get_private_key_from_id
)
from crypto.signer import sign_digest, verify_signature


class TestHashUtils(unittest.TestCase):
    def test_sha256_string(self):
        # Test with string input
        test_str = "hello world"
        result = sha256(test_str)
        self.assertIsInstance(result, bytes)
        self.assertEqual(len(result), 32)  # SHA256 produces 32 bytes

    def test_sha256_bytes(self):
        # Test with bytes input
        test_bytes = b"hello world"
        result = sha256(test_bytes)
        self.assertIsInstance(result, bytes)
        self.assertEqual(len(result), 32)

    def test_sha256_consistency(self):
        # Same input should produce same hash
        test_str = "hello world"
        result1 = sha256(test_str)
        result2 = sha256(test_str)
        self.assertEqual(result1, result2)

    def test_sha256_different_inputs(self):
        # Different inputs should produce different hashes
        result1 = sha256("hello")
        result2 = sha256("world")
        self.assertNotEqual(result1, result2)


class TestKeyManager(unittest.TestCase):
    def setUp(self):
        self.test_output_path = "./tests/keys"
        self.test_signer_id = "test_key_manager"
        # Ensure test directory exists
        os.makedirs(self.test_output_path, exist_ok=True)
        # Backup existing key_registry.json if it exists
        self.registry_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "key_registry.json")
        if os.path.exists(self.registry_path):
            with open(self.registry_path, 'r') as f:
                self.original_registry = json.load(f)
        else:
            self.original_registry = {}

    def tearDown(self):
        # Restore original key_registry.json
        with open(self.registry_path, 'w') as f:
            json.dump(self.original_registry, f, indent=4)
        # Clean up test keys
        for key_file in os.listdir(self.test_output_path):
            if key_file.startswith("private_key_") or key_file.startswith("public_key_"):
                os.remove(os.path.join(self.test_output_path, key_file))

    def test_generate_keypair(self):
        private_key, public_key = generate_keypair(self.test_output_path, self.test_signer_id)
        self.assertIsNotNone(private_key)
        self.assertIsNotNone(public_key)
        
        # Check if files were created
        private_path = os.path.join(self.test_output_path, f"private_key_{self.test_signer_id}.pem")
        public_path = os.path.join(self.test_output_path, f"public_key_{self.test_signer_id}.pem")
        self.assertTrue(os.path.exists(private_path))
        self.assertTrue(os.path.exists(public_path))

    def test_load_keys(self):
        # Generate keys first
        private_key, public_key = generate_keypair(self.test_output_path, self.test_signer_id)
        
        # Test loading private key
        loaded_private = load_private_key(os.path.join(self.test_output_path, f"private_key_{self.test_signer_id}.pem"))
        self.assertIsNotNone(loaded_private)
        
        # Test loading public key
        loaded_public = load_public_key(os.path.join(self.test_output_path, f"public_key_{self.test_signer_id}.pem"))
        self.assertIsNotNone(loaded_public)

    def test_get_keys_from_id(self):
        # Generate keys first
        private_key, public_key = generate_keypair(self.test_output_path, self.test_signer_id)
        
        # Test getting public key from ID
        loaded_public = get_public_key_from_id(self.test_signer_id)
        self.assertIsNotNone(loaded_public)
        
        # Test getting private key from ID
        loaded_private = get_private_key_from_id(self.test_signer_id)
        self.assertIsNotNone(loaded_private)


class TestSigner(unittest.TestCase):
    def setUp(self):
        self.test_output_path = "./tests/keys"
        self.test_signer_id = "test_signer"
        os.makedirs(self.test_output_path, exist_ok=True)
        # Generate test keypair
        self.private_key, self.public_key = generate_keypair(self.test_output_path, self.test_signer_id)
        self.test_message = b"test message"

    def tearDown(self):
        # Clean up test keys
        for key_file in os.listdir(self.test_output_path):
            if key_file.startswith("private_key_") or key_file.startswith("public_key_"):
                os.remove(os.path.join(self.test_output_path, key_file))

    def test_sign_and_verify(self):
        # Test signing
        signature = sign_digest(self.test_message, self.private_key)
        self.assertIsNotNone(signature)
        
        # Test verification
        is_valid = verify_signature(self.test_message, signature, self.public_key)
        self.assertTrue(is_valid)

    def test_verify_invalid_signature(self):
        # Create invalid signature by modifying a valid one
        valid_signature = sign_digest(self.test_message, self.private_key)
        invalid_signature = valid_signature + b"invalid"
        
        # Test verification of invalid signature
        is_valid = verify_signature(self.test_message, invalid_signature, self.public_key)
        self.assertFalse(is_valid)

    def test_verify_different_message(self):
        # Sign one message
        signature = sign_digest(self.test_message, self.private_key)
        
        # Try to verify with different message
        different_message = b"different message"
        is_valid = verify_signature(different_message, signature, self.public_key)
        self.assertFalse(is_valid)


if __name__ == "__main__":
    unittest.main()

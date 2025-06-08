import unittest
from unittest.mock import MagicMock, patch
import os
import tempfile
from storage.ipfs_client import (
    connect_multiaddr,
    add_file,
    get_file,
    pin_file,
    unpin_file,
    resolve_path
)


class TestIPFSClient(unittest.TestCase):
    def setUp(self):
        self.test_multiaddr = "/ip4/127.0.0.1/tcp/5001"
        self.mock_client = MagicMock()
        self.test_cid = "QmTest123"
        
        # Create a temporary test file
        self.temp_dir = tempfile.mkdtemp()
        self.test_file_path = os.path.join(self.temp_dir, "test.txt")
        with open(self.test_file_path, "w") as f:
            f.write("test content")

    def tearDown(self):
        # Clean up temporary files
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
        os.rmdir(self.temp_dir)

    @patch('ipfshttpclient.connect')
    def test_connect_multiaddr(self, mock_connect):
        # Test successful connection
        mock_connect.return_value = self.mock_client
        client = connect_multiaddr(self.test_multiaddr)
        mock_connect.assert_called_once_with(self.test_multiaddr)
        self.assertEqual(client, self.mock_client)

    def test_add_file(self):
        # Test adding a file with provided client
        self.mock_client.add.return_value = {'Hash': self.test_cid}
        result = add_file(self.mock_client, self.test_file_path)
        
        self.mock_client.add.assert_called_once_with(self.test_file_path, pin=True)
        self.assertEqual(result, self.test_cid)

    @patch('storage.ipfs_client.connect_multiaddr')
    def test_add_file_without_client(self, mock_connect):
        # Test adding a file without providing client
        mock_connect.return_value = self.mock_client
        self.mock_client.add.return_value = {'Hash': self.test_cid}
        
        result = add_file(None, self.test_file_path)
        
        mock_connect.assert_called_once()
        self.mock_client.add.assert_called_once_with(self.test_file_path, pin=True)
        self.assertEqual(result, self.test_cid)

    def test_get_file(self):
        # Test getting a file with provided client
        test_data = b"test content"
        self.mock_client.cat.return_value = test_data
        
        output_path = os.path.join(self.temp_dir, "output.txt")
        get_file(self.test_cid, output_path, self.mock_client)
        
        self.mock_client.cat.assert_called_once_with(self.test_cid)
        self.assertTrue(os.path.exists(output_path))
        with open(output_path, 'rb') as f:
            self.assertEqual(f.read(), test_data)
        
        # Clean up
        os.remove(output_path)

    @patch('storage.ipfs_client.connect_multiaddr')
    def test_get_file_without_client(self, mock_connect):
        # Test getting a file without providing client
        mock_connect.return_value = self.mock_client
        test_data = b"test content"
        self.mock_client.cat.return_value = test_data
        
        output_path = os.path.join(self.temp_dir, "output.txt")
        get_file(self.test_cid, output_path)
        
        mock_connect.assert_called_once()
        self.mock_client.cat.assert_called_once_with(self.test_cid)
        self.assertTrue(os.path.exists(output_path))
        with open(output_path, 'rb') as f:
            self.assertEqual(f.read(), test_data)
        
        # Clean up
        os.remove(output_path)

    def test_pin_file(self):
        # Test pinning a file with provided client
        pin_file(self.test_cid, self.mock_client)
        self.mock_client.pin.add.assert_called_once_with(self.test_cid)

    @patch('storage.ipfs_client.connect_multiaddr')
    def test_pin_file_without_client(self, mock_connect):
        # Test pinning a file without providing client
        mock_connect.return_value = self.mock_client
        pin_file(self.test_cid)
        
        mock_connect.assert_called_once()
        self.mock_client.pin.add.assert_called_once_with(self.test_cid)

    def test_unpin_file(self):
        # Test unpinning a file with provided client
        unpin_file(self.test_cid, self.mock_client)
        self.mock_client.pin.rm.assert_called_once_with(self.test_cid)

    @patch('storage.ipfs_client.connect_multiaddr')
    def test_unpin_file_without_client(self, mock_connect):
        # Test unpinning a file without providing client
        mock_connect.return_value = self.mock_client
        unpin_file(self.test_cid)
        
        mock_connect.assert_called_once()
        self.mock_client.pin.rm.assert_called_once_with(self.test_cid)

    def test_resolve_path(self):
        # Test resolving a path with provided client
        resolved_path = "/ipfs/QmResolved123"
        self.mock_client.resolve.return_value = resolved_path
        
        result = resolve_path(self.test_cid, self.mock_client)
        
        self.mock_client.resolve.assert_called_once_with(self.test_cid)
        self.assertEqual(result, resolved_path)

    @patch('storage.ipfs_client.connect_multiaddr')
    def test_resolve_path_without_client(self, mock_connect):
        # Test resolving a path without providing client
        mock_connect.return_value = self.mock_client
        resolved_path = "/ipfs/QmResolved123"
        self.mock_client.resolve.return_value = resolved_path
        
        result = resolve_path(self.test_cid)
        
        mock_connect.assert_called_once()
        self.mock_client.resolve.assert_called_once_with(self.test_cid)
        self.assertEqual(result, resolved_path)


if __name__ == "__main__":
    unittest.main()
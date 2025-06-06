from cryptography.hazmat.primitives import hashes

# Generate a sha256 hash of some data
def sha256(data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    hash = hashes.Hash(hashes.SHA256())
    hash.update(data)
    return hash.finalize()
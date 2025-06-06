from cryptography.hazmat.primitives import hashes

def sha256(data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    hash = hashes.Hash(hashes.SHA256())
    hash.update(data)
    return hash.finalize()
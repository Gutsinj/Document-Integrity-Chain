from hashlib import sha256
from ecdsa import BadSignatureError
from ecdsa.util import sigencode_der, sigdecode_der

# Sign a block header using the user's private key
def sign_digest(digest, private_key):
    sig = private_key.sign_deterministic(
        digest,
        hashfunc=sha256,
        sigencode=sigencode_der
    )

    return sig

# Verify signature was signed by intended user by using their public key
def verify_signature(digest, signature, public_key):
    try:
        isValid = public_key.verify(signature, digest, sha256, sigdecode=sigdecode_der)
        assert isValid
        return True
    except BadSignatureError:
        return False


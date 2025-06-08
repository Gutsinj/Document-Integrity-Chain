from ecdsa import SigningKey, VerifyingKey, SECP256k1
import os
import json

SCRIPT_DIR = os.path.dirname(__file__)
PARENT_DIR = os.path.dirname(SCRIPT_DIR)

# Generate an ecdsa key pair at the output path
def generate_keypair(output_path, signer_id):
    private_key = SigningKey.generate(curve=SECP256k1)
    public_key = private_key.verifying_key

    private_pem = private_key.to_pem(format="pkcs8")
    public_pem = public_key.to_pem(format="pkcs8")

    with open(os.path.join(output_path, "private_key_" + str(signer_id) + ".pem"), "wb") as f:
        f.write(private_pem)

    with open(os.path.join(output_path, "public_key_" + str(signer_id) + ".pem"), "wb") as f:
        f.write(public_pem)

# Load a private key from a PEM file
def load_private_key(private_key_path):
    with open(private_key_path) as f:
        return SigningKey.from_pem(f.read())

# Load a public key from a PEM file
def load_public_key(public_key_path):
    with open(public_key_path) as f:
        return VerifyingKey.from_pem(f.read())

# Load the public key from a signer id
def get_public_key_from_id(signer_id):
    data = None
    with open(os.path.join(PARENT_DIR, "key_registry.json"), "r") as f:
        data = json.load(f)

    return load_public_key(data[str(signer_id)])

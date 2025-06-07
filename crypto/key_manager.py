from ecdsa import SigningKey, VerifyingKey, SECP256k1
import os

# Generate an ecdsa key pair at the output path
def generate_keypair(output_path):
    private_key = SigningKey.generate(curve=SECP256k1)
    public_key = private_key.verifying_key

    private_pem = private_key.to_pem(format="pkcs8")
    public_pem = public_key.to_pem(format="pkcs8")

    with open("private_key.pem", "wb") as f:
        f.write(os.path.join(output_path, private_pem))

    with open("public_key.pem", "wb") as f:
        f.write(os.path.join(output_path, public_pem))

# Load a private key from a PEM file
def load_private_key(private_key_path):
    with open(private_key_path) as f:
        return SigningKey.from_pem(f.read())

# Load a public key from a PEM file
def load_public_key(public_key_path):
    with open(public_key_path) as f:
        return VerifyingKey.from_pem(f.read())
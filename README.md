# Document Integrity Chain

A blockchain-based system for ensuring document integrity and verification. This application allows users to upload documents, which are then stored in IPFS and their hashes are recorded in a blockchain. The system provides document verification capabilities to ensure documents haven't been tampered with.

## Why This Project

I created this project to bring together two key areas of my experience: academic cryptography and real-world legal work. While working at a law firm, I saw firsthand how critical it is to preserve the authenticity of legal documents—especially in sensitive cases where document tampering could undermine trust or jeopardize outcomes. At the same time, my coursework in cryptography introduced me to the technical principles behind secure, verifiable systems. I realized that blockchain, with its immutable structure and decentralized trust model, could be the perfect solution. This project is the result of that convergence—a practical application of cryptographic principles to protect document integrity in a legal context.

## Features

- Document upload and storage in IPFS
- Blockchain-based document hash storage
- Document verification with Merkle proofs
- User authentication and key management
- Web interface for easy interaction

## Prerequisites

- Python 3.8 or higher
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Document-Integrity-Chain
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Set the PYTHONPATH:
```bash
export PYTHONPATH="$(pwd):$PYTHONPATH"
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the Flask application:
```bash
python app.py
```

2. Access the web interface at http://127.0.0.1:5000

## Usage

1. Register with a signer ID
2. Upload documents (system will create blocks after every 2 documents)
3. Verify documents using the verification interface
4. View the blockchain and document history

## Project Structure

- `app.py`: Main application file
- `blockchain/`: Blockchain implementation
- `crypto/`: Cryptographic utilities
- `storage/`: IPFS storage integration
- `templates/`: Web interface templates
- `static/`: Static files (CSS, JS)
- `keys/`: Key storage directory
- `tests/`: Test files
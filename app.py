from flask import Flask, request, jsonify, render_template, flash, redirect, url_for, session
from blockchain.block import Block
from blockchain.chain import Blockchain
from blockchain.merkle_tree import MerkleTree
from crypto.hash_utils import sha256
from crypto.key_manager import get_private_key_from_id, generate_keypair
from storage.ipfs_client import connect_multiaddr, add_file
import time
import os
import tempfile
import logging
import atexit
import glob
import json
from collections import deque

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for flash messages and session
blockchain = Blockchain()

# Ensure keys directory exists
os.makedirs('./keys', exist_ok=True)

# IPFS node address
IPFS_NODE = "/ip4/127.0.0.1/tcp/5002"

# Initialize IPFS client
try:
    ipfs_client = connect_multiaddr(IPFS_NODE)
    logger.info("Successfully connected to IPFS node")
except Exception as e:
    logger.error(f"Failed to connect to IPFS node: {str(e)}")
    ipfs_client = None

# Store pending documents
pending_docs = deque(maxlen=2)

def cleanup_keys():
    """Remove all key files and reset key registry."""
    try:
        # Remove all .pem files from keys directory
        key_files = glob.glob('./keys/*.pem')
        for key_file in key_files:
            os.remove(key_file)
            logger.info(f"Removed key file: {key_file}")
        
        # Reset key registry
        with open('key_registry.json', 'w') as f:
            json.dump({}, f, indent=4)
        logger.info("Reset key registry")
        
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")

# Register cleanup function
atexit.register(cleanup_keys)

def check_credentials(signer_id):
    """Check if a signer has valid credentials."""
    try:
        private_key = get_private_key_from_id(signer_id)
        return private_key is not None
    except (KeyError, FileNotFoundError):
        return False

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        signer_id = request.form.get('signer_id')
        if not signer_id:
            flash('Please enter a signer ID', 'danger')
            return redirect(url_for('index'))
        
        if check_credentials(signer_id):
            flash('Credentials already exist for this signer ID', 'warning')
            return redirect(url_for('index'))
        
        try:
            output_path = './keys'
            generate_keypair(output_path, signer_id)
            session['signer_id'] = signer_id
            flash('Credentials generated successfully', 'success')
            return redirect(url_for('upload'))
        except Exception as e:
            flash(f'Error generating credentials: {str(e)}', 'danger')
            return redirect(url_for('index'))
    
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'signer_id' not in session:
        flash('Please register first', 'warning')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        try:
            # Save file temporarily using system temp directory
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                file.save(temp_file.name)
                file_path = temp_file.name
            
            # Add file to IPFS if client is available
            if ipfs_client:
                try:
                    ipfs_hash = add_file(ipfs_client, file_path)
                    logger.info(f"File added to IPFS with hash: {ipfs_hash}")
                except Exception as e:
                    logger.error(f"Failed to add file to IPFS: {str(e)}")
                    ipfs_hash = f"Qm{sha256(open(file_path, 'rb').read()).hex()[:40]}"
            else:
                logger.warning("IPFS client not available, using mock hash")
                ipfs_hash = f"Qm{sha256(open(file_path, 'rb').read()).hex()[:40]}"
            
            # Calculate file hash
            file_hash = sha256(open(file_path, 'rb').read())
            
            # Add document to pending queue
            doc_info = {
                'hash': file_hash,
                'ipfs_hash': ipfs_hash,
                'file_path': file_path
            }
            pending_docs.append(doc_info)
            
            # If we have two documents, create a new block
            if len(pending_docs) == 2:
                private_key = get_private_key_from_id(session['signer_id'])
                new_block = create_block_from_docs(pending_docs, session['signer_id'], private_key)
                if new_block:
                    flash('Block created successfully', 'success')
                    pending_docs.clear()
                else:
                    flash('Failed to create block', 'danger')
            else:
                flash('Document added to pending queue', 'info')
            
            return redirect(url_for('upload'))
            
        except Exception as e:
            flash(f'Error processing document: {str(e)}', 'danger')
            return redirect(request.url)
        finally:
            if 'file_path' in locals():
                os.unlink(file_path)
    
    return render_template('upload.html', signer_id=session['signer_id'])

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if 'signer_id' not in session:
        flash('Please register first', 'warning')
        return redirect(url_for('index'))
    
    verification_result = None
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        try:
            # Save file temporarily using system temp directory
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                file.save(temp_file.name)
                file_path = temp_file.name
            
            # Calculate file hash
            file_hash = sha256(open(file_path, 'rb').read())
            
            # Verify file in blockchain
            exists, block_index = blockchain.verify_file_in_blockchain(file_hash)
            
            if exists:
                # Get merkle proof
                proof, _ = blockchain.get_file_proof(file_hash)
                block = blockchain.chain[block_index]
                
                verification_result = {
                    'verified': True,
                    'block_index': block_index,
                    'block_hash': block.hash.hex(),
                    'merkle_proof': [
                        {
                            'hash': p['hash'].hex(),
                            'direction': p['direction']
                        } for p in proof
                    ]
                }
            else:
                verification_result = {
                    'verified': False,
                    'message': 'Document not found in blockchain'
                }
            
        except Exception as e:
            flash(f'Error verifying document: {str(e)}', 'danger')
        finally:
            if 'file_path' in locals():
                os.unlink(file_path)
    
    return render_template('verify.html', signer_id=session['signer_id'], verification_result=verification_result)

@app.route('/chain')
def view_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append({
            'index': block.index,
            'timestamp': block.timestamp,
            'merkle_root': block.merkle_root.hex() if isinstance(block.merkle_root, bytes) else block.merkle_root,
            'prev_hash': block.prev_hash.hex() if isinstance(block.prev_hash, bytes) else block.prev_hash,
            'signer_id': block.signer_id,
            'hash': block.hash.hex() if isinstance(block.hash, bytes) else block.hash
        })
    
    return render_template('chain.html', chain=chain_data)

def create_block_from_docs(docs, signer_id, private_key):
    """Create a new block from a list of documents."""
    # Create merkle tree with all document hashes
    merkle_tree = MerkleTree([doc['hash'] for doc in docs])
    
    # Create and add new block
    latest_block = blockchain.get_latest_block()
    new_block = Block(
        latest_block.index + 1,
        time.time(),
        merkle_tree,
        latest_block.compute_hash(),
        signer_id,
        private_key
    )
    
    if blockchain.add_block(new_block):
        return new_block
    return None

if __name__ == '__main__':
    app.run(debug=True, port=5001) 
import subprocess
import time
import os
import signal
import atexit

class IPFSDaemon:
    def __init__(self):
        self.process = None
        atexit.register(self.cleanup)

    def start(self):
        if self.process is None:
            try:
                # Start IPFS daemon
                self.process = subprocess.Popen(
                    ['ipfs', 'daemon'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    preexec_fn=os.setsid
                )
                # Wait for daemon to start
                time.sleep(5)
                return True
            except Exception as e:
                print(f"Failed to start IPFS daemon: {e}")
                return False
        return True

    def stop(self):
        if self.process:
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                self.process = None
            except Exception as e:
                print(f"Failed to stop IPFS daemon: {e}")

    def cleanup(self):
        self.stop()

def run_ipfs_command(command):
    """Run an IPFS command and return the output"""
    try:
        result = subprocess.run(['ipfs'] + command, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"IPFS command failed: {e}")
        return None

# Add a file to IPFS
def add_file(file_path):
    result = run_ipfs_command(['add', '-Q', file_path])
    return result

# Get a file from IPFS
def get_file(cid, output_path):
    try:
        result = subprocess.run(['ipfs', 'get', cid, '-o', output_path], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to get file: {e}")
        return False

# Pin a file to IPFS
def pin_file(cid):
    return run_ipfs_command(['pin', 'add', cid])

# Unpin a file from IPFS
def unpin_file(cid):
    return run_ipfs_command(['pin', 'rm', cid])

# Resolve a path to a CID
def resolve_path(cid):
    return run_ipfs_command(['resolve', cid])
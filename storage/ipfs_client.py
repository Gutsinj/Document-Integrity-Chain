import ipfshttpclient

# Connect to IPFS node
def connect_multiaddr(multiaddr):
    return ipfshttpclient.connect(multiaddr)

# Add a file to IPFS
def add_file(client, file_path):
    client = client or connect_multiaddr()
    res = client.add(file_path, pin=True)
    return res['Hash']

# Get a file from IPFS
def get_file(cid, output_path, client=None):
    client = client or connect_multiaddr()
    data = client.cat(cid)
    with open(output_path, 'wb') as f:
        f.write(data)

# Pin a file to IPFS
def pin_file(cid, client=None):
    client = client or connect_multiaddr()
    client.pin.add(cid)

# Unpin a file from IPFS
def unpin_file(cid, client=None):
    client = client or connect_multiaddr()
    client.pin.rm(cid)

# Resolve a path to a CID
def resolve_path(cid, client=None):
    client = client or connect_multiaddr()
    return client.resolve(cid)
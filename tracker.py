import os
import sys

import bencodepy as bencode
import requests

class Tracker:
    def __init__(self, info_hash, url):
        self.info_hash = info_hash
        self.url = url
        self.peer_id = b'--BCLI--' + os.urandom(12)
        self.addresses = []
        
    def start(self):
        params = {
            'info_hash': self.info_hash,
            'peer_id': self.peer_id,
            'port': 6881,
            'uploaded': 0,
            'downloaded': 0,
            'event': 'started',
        }
        response = requests.get(url = self.url, params = params)
        response = dict(bencode.bdecode(response.content).items())
        
        if 'failure reason' in response:
            print("Razão da falha:", response['failure reason'])
            sys.exit()
        if 'peers' not in response:
            print('Razão da falha', 'Sem peers')
            sys.exit()
            
        peers = [response['peers'][i : i + 6] for i in range(0, len(response['peers']), 6)]
        for peer in peers:
            ip = '.'.join(str(i) for i in peer[:4])
            port = int.from_bytes(peer[-2:], 'big')
            self.addresses.append((ip, port))

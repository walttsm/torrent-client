import socket
import struct
import sys
import threading

import bitstring

import cli
import config

class Peer(threading.Thread):
    def __init__(self, address):
        threading.Thread.__init__(self)
        self.address = address
        self.socket = socket.socket()
        self.socket.settimeout(10)
        self.state = {
            'handshake': False,
            'choking': True,
        }
      
      
    """
    Conecta ao endereço
    """    
    def connect(self):
        try:
            self.socket.connect(self.address)
        except OSError as _:
            self.disconnect()
            
            
    """
    Desconecta do endereço
    """
    def disconnect(self):
        self.socket.close()
        config.manager.disconnect(self.address)
        sys.exit()
        
    """
    Roda o programa
    """
    def run(self):
        self.connect()
        self.send_handshake()
        self.parse_stream()
        
    """
    Determina o caminho da stream
    """
    def parse_stream(self):
        stream = b''
        while True:
            try:
                packet = self.socket.recv(4096)
            except OSError as e:
                self.printf('Falha ao receber{}'.format(e))
                self.disconnect()
                
            if not packet:
                self.printf('Pacote vazio')
                self.disconnect()
                
            if not self.state['handshake']:
                self.printf('Handshake')
                packet = self.handle_handshake(packet)
                
            stream_complete = True
            
            stream += packet
            while len(stream) >= 4:
                length = struct.unpack('>I', stream[:4])[0]
                if length == 0 or len(stream) < length + 4:
                    self.send(bytes(4))
                    stream_complete = False
                    break
                message = stream[4 : length+4]
                self.handle(message)
                stream = stream[length + 4:]
                
            if stream_complete:
                if self.state['choking']:
                    self.send_interested()
                else:
                    self.send_request()
                    
    def handle(self, message):
        if message[0] == 0:
            self.state['choking'] = True
        elif message[0] == 1:
            self.state['choking'] = False
        elif message[0] == 4:
            self.handle_have(message[1:])
        elif message[0] == 5:
            self.handle.bitfield(message[1:])
        elif message[0] == 7:
            self.handle_block(message[1:])
            
    def handle_handshake(self, packet):
        pstrlen = packet[0]
        
        # Validando tamanho do pacote
        if len(packet) < pstrlen + 29:
            self.printf('Short handshake')
            self.disconnect()
            
        info_hash = struct.unpack('>20s', packet[pstrlen + 9 : pstrlen+ 29])[0]
        
        # Validando handshake
        if info_hash != config.tracker.info_hash:
            self.printf('Info hashes não são iguais')
            self.disconnect()
            
        self.state['handshake'] = True
        return packet[pstrlen + 49:]
    
    def handle_have(self, payload):
        # Validação de tamanho
        if len(payload) < 4:
            self.printf('Short have')
            self.disconnect()
            
        piece_idx = struct.unpack('>I', payload)[0]
        config.manager.has(self.address, piece_idx)
        
    def handle_bitfield(self, payload):
        bit_array = list(bitstring.BitArray(payload))
        for piece_idx, available in enumerate(bit_array):
            if available:
                config.manager.has(self.address, piece_idx)
                
    def handle_block(self, payload):
        # Validação de tamanho
        if len(payload) < 8:
            self.printf('Short Block')
            self.disconnect()
        
        piece_idx, block_idx = struct.unpack('>II', payload[:8])
        block = payload[8:]
        success = config.manager.push(self.address, piece_idx, block_idx, block)
        if not success:
            self.disconnect()
        
    def send(self, message):
        if not message:
            self.disconnect()
            
        try:
            self.socket.send(message)
        except OSError as _:
            return
        
    def send_handshake(self):
        pstr = b'Protocolo Bittorrent'
        pstr_length = bytes([len(pstr)])
        reserved = bytes(8)
        self.send(pstr_length + pstr + reserved + config.tracker.info_hash + config.tracker.peer_id)
        
        
    def send_interested(self):
        self.send(b'\x00\x00\x00\x01\x02')
    
    def send_request(self):
        self.send(config.manager.next(self.address))
        
    def printf(self, message):
        cli.printf(message, prefix=self.address[0])
            
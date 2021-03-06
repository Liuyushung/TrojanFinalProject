#! python
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 18:53:33 2020

@author: 劉又聖
"""

# Encapsulate nbyte_to_data(),data_to_nbyte to a class NetworkIO
import struct

class NetworkIO:
    def __init__(self, sock):
        self.handle = sock
    def read_handle(self, n):
        return self.handle.recv(n)      # sock.recv(n)
    def write_handle(self, d):
        return self.handle.send(d)      # sock.send(d)
    def data_to_nbyte(self, n):
        if isinstance(n, int):      # type(n) == int
            if n < (1<<8):          # 0~255
                tag = b'B'
            elif n < (1<<16):       # 256~65535
                tag = b'H'
            elif n < (1<<32):       # 65536~4294967295
                tag = b"L"
            else:                   # 4294967296~
                tag = b'Q'
            result = tag + struct.pack('!' + tag.decode(), n)
            return result
        elif isinstance(n, float):
            result = b'd' + struct.pack('!d', n)
            return result
        elif isinstance(n, bytes):
            result = b's' + self.data_to_nbyte(len(n)) + n
            return result
        elif isinstance(n, str):
            n = n.encode('UTF-8')
            result = b'c' + self.data_to_nbyte(len(n)) + n
            return result
        raise TypeError('Invalid type: ' + str(type(n)) )
    
    def nbyte_to_data(self):
        size_info = { 'B':1, 'H':2, 'L':4, 'Q':8, 'd':8 }
    
        btag = self.read_raw(1)         # read 1 byte
        if not btag:
            return None
        else:
            tag = btag.decode('UTF-8')
    
        if tag in size_info:                
            size    = size_info[tag]
            bnum    = self.read_raw(size)      
            result  = struct.unpack('!' + tag, bnum)[0] 
        elif tag in "sc":
            size    = self.nbyte_to_data()   
            if size >= 65536:
                raise ValueError('length too long: ' + str(size))
            bstr    = self.read_raw(size)
            result  = bstr if tag == 's' else bstr.decode('UTF-8')
        else:
            raise TypeError('Invalid type: ' + tag)
        return result
    def read_raw(self, n):
        return self.read_handle(n)
    def write_raw(self, d):
        return self.write_handle(d)
    def read(self):
        return self.nbyte_to_data()
    def write(self, d):
        byte_data = self.data_to_nbyte(d)
        self.write_raw(byte_data)
    def close_handle(self):
        return self.handle

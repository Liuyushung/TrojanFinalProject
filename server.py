#! python
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 19:55:13 2020

@author: 劉又聖
"""

import socket, platform, sys, os
import logging

from networkAPI import NetAPI, save_file
from config import server_save_dir, set_logging
from pprint import pprint

set_logging()

def server(host, port):
    listeningSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listeningSock.bind( (host, port) )
    listeningSock.listen()
    print("Listening at", listeningSock.getsockname())

    while True:
        logging.debug('Wait somebody...')
        sock, sockname = listeningSock.accept()
        handle = NetAPI(sock)
        logging.debug('Conn with {}'.format(sockname))
        while True:
            data = handle.recv_file()   # It will receive a dict
            if not data:    break
            pprint(data)
            save_file(data, os.path.join(server_save_dir.get(platform.system()),
                                         str(sockname[0])))
        sock.close()

    listeningSock.close()

def main():
    msg = "Usage: %s host port" % sys.argv[0]
    if len(sys.argv) != 3:
        print(msg)
    else:
        host = sys.argv[1]
        port = int(sys.argv[2])
        server(host, port)

if __name__ == "__main__":
    main()
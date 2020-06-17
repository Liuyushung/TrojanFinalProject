#! python
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 19:55:13 2020

@author: 劉又聖
"""

import socket, sys, os

from networkAPI import NetAPI, save_file

def server(host, port):
    listeningSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listeningSock.bind( (host, port) )
    listeningSock.listen()
    print("Listening at", listeningSock.getsockname())

    while True:
        sock, sockname = listeningSock.accept()
        handle = NetAPI(sock)
        while True:
            data = handle.recv_file()   # It will receive a dict
            if not data:
                break
            print('receive  from {}\n{}'.format(sockname, data))
            save_file(data, os.path.join(NetAPI.savePath, str(sockname[0])))
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
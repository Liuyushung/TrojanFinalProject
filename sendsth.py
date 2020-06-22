#! python
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 15:03:09 2020

@author: 劉又聖
"""

import os, logging

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

def send_dir(handle, dir_paths, isEndFlag):
    if isinstance(dir_paths, (list, tuple)):
        for dir_path in dir_paths:
            for file in scan_dir_and_cktime(dir_path).keys():
                handle.send_file(file)
    elif isinstance(dir_paths, str):
        pass
    
    isEndFlag.wait()  # 做最後一次傳送
    if isinstance(dir_paths, (list, tuple)):
        for dir_path in dir_paths:
            for file in scan_dir_and_cktime(dir_path).keys():
                handle.send_file(file)
    
    return None
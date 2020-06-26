#! python
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 15:03:09 2020

@author: 劉又聖
"""

import os, logging, json

def cal_cksum(fname):
    ''' Calculate the checksume of file with sha256 '''
    from hashlib import sha256
    
    s = sha256()
    with open(fname, 'rb') as fd:
        for chunk in iter(lambda : fd.read(1024), b''):
            s.update(chunk)
    return s.hexdigest()

def get_pre_infos(fname):
    if not os.path.exists(fname):
        return {}
    else:
        with open(fname, 'r') as fd:
            return json.load(fd)

def get_file_infos(fname):
    '''
    Parameters
    ----------
    fname : TYPE string
        the fullpath of file.

    Returns
    -------
    dict
        'fsize' : file size,
        'mtime' : the last modify time,
        'cksum' : file checksum,
    '''
    assert os.path.exists(fname), '{} is not exist.'.format(fname)
    
    fsize = os.path.getsize(fname)
    mtime = os.path.getmtime(fname)
    cksum = cal_cksum(fname)
    
    return {'fsize' : fsize, 'mtime' : mtime, 'cksum' : cksum}

def scan_dir(path):
    '''
    Parameters
    ----------
    path : TYPE string
        the directory path

    Yields
    ------
    TYPE string
        the fullpath of file
    '''
    if os.path.exists(path):
        if os.path.isdir(path):
            # This path is directory
            for filename in os.listdir(path):
                fullpath = os.path.join(path, filename)
                yield from scan_dir(fullpath)
        else:
            # This path is file
            yield path
    
#TODO 寫個check file routine
def scan_dir_and_ckchanged(dir_path):
    from config import client_save_dirs
    import platform
    
    # Generate the local folder storing the tmp file
    local_save_dir = client_save_dirs.get(platform.system())
    if not os.path.exists(local_save_dir):
        os.makedirs(local_save_dir)
    # Generate previous file & Get previous file infos
    previous_fname = os.path.join(local_save_dir, 'previous.json')
    previous_status = get_pre_infos(previous_fname)
    
    if not previous_status:
        first_flag = True   # 沒有資料，為第一次讀取
    else:
        first_flag = False  # 有資料
        
    # 開始檢查目錄下的所有檔案
    update_list = {}
    for file in scan_dir(dir_path):
        file_infos = get_file_infos(file)
        # Check that file if had been changed.
        if previous_status.get(file) != file_infos:
            update_list[file] = file_infos
            previous_status[file] = file_infos
    
    # Save file infos into previous.json
    with open(previous_fname, 'w') as fd:
        if first_flag:
            json.dump(update_list, fd)
        else:
            json.dump(previous_status, fd)
    
    return update_list
        
def send_dir(handle, dir_paths, isEndFlag):
    '''
    This is API for sending directory.

    Parameters
    ----------
    handle : TYPE NetworkAPI
        Deal the send file
    dir_paths : list or tuple
        contain the upload directory.
    isEndFlag : TYPE Threading.Event
        Detect the program if is end.

    Returns
    -------
    None.
    '''
    try:
        if isinstance(dir_paths, (list, tuple)):
            for dir_path in dir_paths:
                for file in scan_dir_and_ckchanged(dir_path).keys():
                    handle.send_file(file)
        elif isinstance(dir_paths, str):
            pass
    
        if not isEndFlag.is_set():
            isEndFlag.wait()  # 等待做最後一次傳送
            send_dir(handle, dir_paths, isEndFlag)    
            logging.debug('Send dir out')    
    except KeyboardInterrupt:
        logging.debug('catch Ctrl+C in {}'.format(__name__))
    except Exception as e:
        logging.error('Unknown Error: {}'.format(e.args))
        pass
    
    return None

#TODO check the delete file

if __name__ == '__main__':
    # Debug
    from glob import glob
    
    for name in glob('*'):
        if os.path.isfile(name):
            print(name, cal_cksum(name), sep=': ')
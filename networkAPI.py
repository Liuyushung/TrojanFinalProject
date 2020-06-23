#! python
# -*- coding: utf-8 -*-
"""
Created on Tue May 26 20:14:03 2020

@author: 劉又聖
"""

# Define a class NetAPI to utilize NetworkIO to send/recv data.
import os, shutil, logging, platform

logging.basicConfig(level=logging.DEBUG, format='%(levelname)5s:%(message)s')

def split_path(path):
    """ Return List of path """
    import os
    
    result = []
    
    while True:
        head, tail = os.path.split(path)
        if tail:
            result.insert(0, tail)
            path = head
        else:
            head = head.strip(':/\\')
            if head:
                result.insert(0, head)
            break
            
    return result

def normalize_name(path):
    """ Return the path connected with '/' """
    path_list = split_path(path)
    result = '/'.join(path_list)
    return result

def change_file_mtime(file, mtime):
    assert os.path.exists(file), 'FileNotExists: {}'.format(file)
    os.utime(file, (mtime, mtime))
    return True

def verify_checksum(file, cksum):
    from sendsth import cal_cksum
    return cal_cksum(file) == cksum if True else False
    
def save_file(file_info, dirctory):
    file_name = file_info.get(NetAPI.FILE_NAME_TAG)
    file_size = file_info.get(NetAPI.FILE_SIZE_TAG)
    file_mtime = file_info.get(NetAPI.FILE_MTIME_TAG)
    file_cksum = file_info.get(NetAPI.FILE_CKSUM_TAG)
    file_content = file_info.get(NetAPI.FILE_CONTENT_TAG)
    tmp_file_name = file_info.get(NetAPI.FILE_BLOCK_TAG)
    
    if not file_name or not file_size or not file_mtime or not file_cksum:
        return False
    if not file_content and not tmp_file_name:
        return False
    else:
        full_name = os.path.join(dirctory, file_name)
        dir_name  = os.path.dirname(full_name)
        
        if not os.path.exists(dir_name):
            logging.info(f'Create new directory {dir_name}')
            os.makedirs(dir_name)
        if file_content:  # 小檔案
            assert file_size == len(file_content), 'File size mismatch. {}'.format(file_name)
            with open(full_name, 'wb') as fd:
                logging.warning('Overwriting existing file {}'.format(file_name))
                fd.write(file_content)
        else:  # 以 Block 傳送，改暫存檔名
            assert os.path.getsize(tmp_file_name) == file_size, 'File size mismatch.'
            shutil.move(tmp_file_name, full_name)  # Change the file name
    
    assert verify_checksum(full_name, file_cksum), 'FileBroken, checksum mismatch.'
    change_file_mtime(full_name, file_mtime)

    return True
            
class NetAPI:
    from config import server_save_dir
    # Control Tag
    FILE_TAG_SIZE       = 8
    FILE_END_TAG        = b'FILEEND0'
    FILE_ABORT_TAG      = b'FILEABRT'
    # Data Tag
    FILE_NAME_TAG       = b'FILENAME'
    FILE_SIZE_TAG       = b'FILESIZE'
    FILE_CONTENT_TAG    = b'FILEDATA'
    FILE_BLOCK_TAG      = b'FILEBLCK'
    FILE_MTIME_TAG      = b'FILETIME'
    FILE_CKSUM_TAG      = b'FILECKSM'
    
    TYPE_ERROR_TEMP     = 'TypeError: Invaild {} type {}'
    
    savePath            = server_save_dir.get(platform.system())
    
    
    def __init__(self, iHandle=None, oHandle=None):
        if not iHandle:
            iHandle     = b''
        if not oHandle:
            oHandle     = iHandle
        from networkio import NetworkIO
        self.iHandle    = NetworkIO(iHandle)
        self.oHandle    = NetworkIO(oHandle)
        self.maxSize    = 2147483647                 # Save file max size
        self.blockSize  = 4096                       # block size

    def send_tag(self, tag):
        #logging.debug('Send tag')
        self.oHandle.write_raw(tag)
        
    def recv_tag(self):
        #logging.debug('Recv tag')
        return self.iHandle.read_raw(self.FILE_TAG_SIZE)

    def send_data(self, data):
        #logging.debug('Send data')
        self.oHandle.write(data)
        
    def recv_data(self):
        #logging.debug('Recv data')
        return self.iHandle.read()

    def send_size(self, n):
        #logging.debug('Send size')
        return self.send_data(n)
    
    def recv_size(self):
        #logging.debug('Recv size')
        size = self.recv_data()
        assert isinstance(size, int), self.TYPE_ERROR_TEMP.format('size', type(size))
        return size

    def send_name(self, s):
        #logging.debug('Send name')
        return self.send_data(s)
    
    def recv_name(self):
        #logging.debug('Recv name')
        path = self.recv_data()
        assert isinstance(path, str), self.TYPE_ERROR_TEMP.format('name', type(path))
        return path
    
    def send_mtime(self, f):
        return self.send_data(f)
    
    def recv_mtime(self):
        mtime = self.recv_data()
        assert isinstance(mtime, float), self.TYPE_ERROR_TEMP.format('mtime', type(mtime))
        return mtime
    
    def send_cksum(self, s):
        return self.send_data(s)
    
    def recv_cksum(self):
        cksum = self.recv_data()
        assert isinstance(cksum, str), self.TYPE_ERROR_TEMP.format('checksum', type(cksum))
        return cksum
    
    def send_content(self, d):
        #logging.debug('Send content')
        return self.send_data(d)
    
    def recv_content(self):
        #logging.deubg('Recv content')
        return self.recv_data()

    def send_file(self, path):
        from sendsth import get_file_infos
        
        file_infos = get_file_infos(path)
        
        filename  = path
        filesize  = file_infos['fsize']
        filemtime = file_infos['mtime']
        filecksum = file_infos['cksum']
        try:
            self.send_tag(self.FILE_NAME_TAG)
            self.send_name(filename)                  # 送檔名
            self.send_tag(self.FILE_SIZE_TAG)
            self.send_size(filesize)                  # 送檔案大小
            self.send_tag(self.FILE_MTIME_TAG)
            self.send_mtime(filemtime)                # 送檔案最後修改時間
            self.send_tag(self.FILE_CKSUM_TAG)
            self.send_cksum(filecksum)                # 送檔案雜湊值
            
            if filesize > self.blockSize:
                self.send_tag(self.FILE_BLOCK_TAG)
                self.send_block(path)                 # 太大送 Block
            else:
                filedata = open(path, 'rb').read()
                self.send_tag(self.FILE_CONTENT_TAG)
                self.send_content(filedata)           # 不大直接送
            
            self.send_tag(self.FILE_END_TAG)
            return True
        except Exception as e:
            print(str(e))
            self.send_tag(self.FILE_ABORT_TAG)
            return False

    def recv_file(self):
        result = {}
        while True:
            tag = self.recv_tag()
            if not tag or tag in [self.FILE_END_TAG, self.FILE_ABORT_TAG]: break
            
            if tag == self.FILE_BLOCK_TAG:
                """ 接收 Block """
                tmp_file_name = self.recv_block()
                result[tag] = tmp_file_name
            else:
                """ 接收一般檔案 """
                data = self.recv_data()
                if not data: break
                # print(tag, data)
                if tag == self.FILE_NAME_TAG:
                    data = normalize_name(data)
                    if '..' in data:
                        raise ValueError('Dangerous Path {}'.format(data))
                result[tag] = data
        return result

    def send_block(self, path):
        #logging.debug('Send block')
        block_ID = 0
        total_size = 0
        
        with open(path, 'rb') as fd:
            while True:
                block = fd.read(self.blockSize)  # 讀取一小塊
                if not block: break
                block_ID += 1
                self.send_data(block_ID)  # 送出區塊編號
                self.send_data(block)     # 送出區塊內容
                total_size += len(block)
            self.send_data(0)  # 傳送區塊結束
        
        return total_size  # 回傳送出區塊的大小
    
    def recv_block(self):
        #logging.debug('Recv block')
        import time
        
        total_size = 0
        last_block = 0
        file_name  = os.path.join(NetAPI.savePath, 'TEMP{}'.format(int(time.time())))
        dirname    = os.path.dirname(file_name)
        
        if not os.path.exists(dirname):
            os.makedirs(dirname)
            
        with open(file_name, 'wb') as fd:
            while True:
                block_ID = self.recv_data()

                assert isinstance(block_ID, int), "TypeError block_ID is not int"
                
                if block_ID == 0:  # 收到結束的 block ID
                    break

                assert last_block + 1 == block_ID, "ValueError block_ID is wrong"
                
                last_block = block_ID
                block = self.recv_data()  # 收 block

                assert isinstance(block, bytes), "TypeError block is not bytes"
                assert len(block) + total_size <= self.maxSize, "RuntimeError size overflow"
                
                fd.write(block)
        
        return file_name
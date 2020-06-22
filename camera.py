#! python
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 20 17:08:58 2020

@author: 劉又聖
"""
import os
import time
import logging
import cv2 as cv
from glob import glob
from config import set_logging

set_logging()

def video_main(save_dir, error_log=''):
    # Make the video save dir
    save_dir = os.path.join(save_dir, '.ccv')
    if not os.path.exists(save_dir):
        logging.info('Create new dir {}'.format(save_dir))
        os.makedirs(save_dir)
    # Set the file name
    num = len(glob(os.path.join(save_dir, 'C' + time.strftime('%Y%m%d') + '*' )))
    fn  = 'C' + time.strftime('%Y%m%d') + str(num) + '.avi'
    fullname = os.path.join(save_dir, fn)
    logging.debug('Save file name is {}'.format(fullname))    
    # Catch the camera
    cap = cv.VideoCapture(0)
    assert cap.isOpened(), "Cannot open camera"
    
    fourcc = cv.VideoWriter_fourcc(*'XVID') # MPEG-4編碼
    out = cv.VideoWriter(fullname, fourcc, 20.0, (640,480))
    
    try:
        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()  # ret 判斷是否有抓到frame
    
            # if frame is read correctly ret is True
            assert ret, "Can't receive frame (stream end?). Exiting ..."
    
            # Save to file
            out.write(frame)
            
            # Our operations on the frame come here
            #gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            # Display the resulting frame
            #cv.imshow('frame', gray)
            #if cv.waitKey(1) == ord('q'):    break
    except KeyboardInterrupt:
        logging.info('Catch Ctrl+C in {}'.format(__name__))
    except Exception as e:
        logging.error(e.args)
        pass
    
    # When everything done, release the resource
    cap.release()
    out.release()
    cv.destroyAllWindows()
    return True

if __name__ == '__main__':
    video_main('D:\\Tmp\\SaveFiles\\Local')
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 23 14:50:34 2013

@author: gonca_000
"""

import cv2
import bisect
import numpy as np

class video:        
    def __init__(self, videopath, timepath):
        self.path = videopath
        self.capture = cv2.VideoCapture(videopath)
        self.timestamps = np.genfromtxt(timepath,dtype=str)
        
    def __del__(self):
        del self.capture
        
    def frameindex(self, timestr):
        return bisect.bisect_left(self.timestamps,timestr)
        
    def frame(self, frameindex):
        self.capture.set(cv2.cv.CV_CAP_PROP_POS_FRAMES,frameindex)
        result,frame = self.capture.read()
        return frame
        
    def movie(self, framestart, frameend):
        self.capture.set(cv2.cv.CV_CAP_PROP_POS_FRAMES,framestart)
        while self.capture.get(cv2.cv.CV_CAP_PROP_POS_FRAMES) < frameend:
            result,frame = self.capture.read()
            if result:
                yield frame
            else:
                break
            
def mvshow(winname, frames, interval = 1000.0 / 25, stepkey = -1):
    for frame in frames:
        key = None
        cv2.imshow(winname,frame)
        while key != stepkey:
            key = cv2.waitKey(interval)
        if key == 27: # Escape
            break
    cv2.destroyWindow(winname)
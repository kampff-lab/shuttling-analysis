# -*- coding: utf-8 -*-
"""
Created on Sat Nov 23 14:50:34 2013

@author: gonca_000
"""

import os
import cv2
import numpy as np
import pandas as pd
import activitymovies

class video:        
    def __init__(self, videopath, timepath=None):
        self.path = videopath
        self.capture = cv2.VideoCapture(videopath)
        if timepath is not None:
            self.timestamps = pd.read_csv(timepath,
                                          sep=' ',
                                          header=None,
                                          names=['time'],
                                          parse_dates=[0],
                                          usecols=[0]).values.flatten()
        else:
            self.timestamps = None
        
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, tb):
        self.release()
        
    def release(self):
        self.capture.release()
        
    def frametime(self, frameindex):
        if self.timestamps is None:
            raise ValueError("video does not have timestamps")
        return self.timestamps[frameindex]
        
    def frameindex(self, time):
        if self.timestamps is None:
            raise ValueError("video does not have timestamps")
        return self.timestamps.searchsorted(np.datetime64(time))
        
    def frame(self, frameindex):
        self.capture.set(cv2.cv.CV_CAP_PROP_POS_FRAMES,frameindex)
        result,frame = self.capture.read()
        return frame
        
    def background(self, frameindex):
        if self.timestamps is None:
            raise ValueError("video does not have timestamps")
        frametime = self.frametime(frameindex)
        vidfolder = os.path.split(self.path)[0]
        backfolder = os.path.join(vidfolder,r'Analysis\Background')
        return activitymovies.getbackground(backfolder,frametime)
        
    def movie(self, framestart, frameend):
        self.capture.set(cv2.cv.CV_CAP_PROP_POS_FRAMES,framestart)
        while self.capture.get(cv2.cv.CV_CAP_PROP_POS_FRAMES) < frameend:
            result,frame = self.capture.read()
            if result:
                yield frame
            else:
                break
            
def readsingleframe(videopath,frameindex,segmented=False):
    timepath = None
    if segmented:
        timepath = os.path.splitext(videopath)[0] + ".csv"

    with video(videopath,timepath) as vid:
        frame = vid.frame(frameindex)
        if segmented:
            background = vid.background(frameindex)
            cv2.subtract(frame,background,frame)
        return frame
        
def readsinglebackground(videopath,frameindex):
    timepath = os.path.splitext(videopath)[0] + ".csv"
    with video(videopath,timepath) as vid:
        return vid.background(frameindex)

def readframe(movie):
    index = movie.capture.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)
    result, frame = movie.capture.read()
    cv2.putText(frame,str(int(index)),(0,30),
                cv2.cv.CV_FONT_HERSHEY_COMPLEX,1,
                (255,255,255,255))
    return frame, index
            
def showmovie(movie,framestart=0,fps=0,frameend=None):
    key = 0
    interval = 0 if fps == 0 else int(1000.0 / fps)
    movie.capture.set(cv2.cv.CV_CAP_PROP_POS_FRAMES,framestart)
    frame, index = readframe(movie)
    while key != 27:
        cv2.imshow('win',frame)
        key = cv2.waitKey(interval)
        if key == 32: #space
            if interval > 0:
                interval = 0
            else:
                interval = 0 if fps == 0 else int(1000.0 / fps)
        if key == 2555904 or key < 0: #right arrow
            frame, index = readframe(movie)
            if index == frameend:
                interval = 0
            continue
        elif key == 2424832: #left arrow
            movie.capture.set(cv2.cv.CV_CAP_PROP_POS_FRAMES,index-1)
            frame, index = readframe(movie)
        elif key == 2228224: #page down
            movie.capture.set(cv2.cv.CV_CAP_PROP_POS_FRAMES,index+10)
            frame, index = readframe(movie)
        elif key == 2162688: #page up
            movie.capture.set(cv2.cv.CV_CAP_PROP_POS_FRAMES,index-10)
            frame, index = readframe(movie)
    cv2.destroyWindow('win')
            
def mvshow(winname, frames, interval = 1000.0 / 25, stepkey = -1):
    for frame in frames:
        key = None
        cv2.imshow(winname,frame)
        while key != stepkey:
            key = cv2.waitKey(interval)
        if key == 27: # Escape
            break
    cv2.destroyWindow(winname)
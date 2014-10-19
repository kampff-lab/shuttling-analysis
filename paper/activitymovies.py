# -*- coding: utf-8 -*-
"""
Created on Sun Sep 28 11:31:29 2014

@author: Gonçalo
"""

import os
import cv2
import bisect
import pandas as pd

datafolder = r'E:/Protocols/Shuttling/LightDarkServoStable/Data'

class framesiterable:
    def __init__(self, path, start, stop):
        self.path = path
        self.start = start
        self.stop = stop
        
    def __iter__(self):
        capture = cv2.VideoCapture(self.path)
        capture.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, self.start)
        try:
            for i in range(self.start, self.stop):
                ret, frame = capture.read()
                if not ret:
                    break
                yield frame
        finally:
            capture.release()
            
def getrelativepath(sessioninfo,path):
    info = sessioninfo.dirname.reset_index()
    return info.apply(lambda x:os.path.join(datafolder,
                                            x.subject,
                                            x.dirname,
                                            path),axis=1)

def getmoviepath(sessioninfo):
    return getrelativepath(sessioninfo,'front_video.avi')
                                            
def gettimepath(sessioninfo):
    return getrelativepath(sessioninfo,'front_video.csv')
                                            
def getbackgroundpath(sessioninfo):
    return getrelativepath(sessioninfo,r'Analysis\Background')
    
def getbackground(path,time):
    files = [f for f in os.listdir(path) if f.startswith('background_')]
    backgroundtimes = [os.path.splitext(f)[0].split('_',1)[1].replace('_',':')
                       for f in files]
    index = bisect.bisect_left(backgroundtimes,time)
    index = min(len(files)-1,index)
    backgroundpath = os.path.join(path, files[index])
    return cv2.imread(backgroundpath, cv2.cv.CV_LOAD_IMAGE_GRAYSCALE)

def getcrossingframes(crossings,sessioninfo):
    crossinginfo = crossings.join(sessioninfo.dirname).reset_index()
    sessions = []
    for (subject,dirname),group in crossinginfo.groupby(['subject','dirname']):
        path = os.path.join(datafolder, subject, dirname, 'front_video.avi')
        path = os.path.normpath(path)
        videos = []
        for crossing in group.slices:
            startframe = crossing.start
            stopframe = crossing.stop
            videos.append(framesiterable(path, startframe, stopframe))
        if len(videos) == 1:
            videos = videos[0]
        sessions.append(videos)
        
    if len(sessions) == 1:
        sessions = sessions[0]
    return sessions
        
def showmovie(movie,fps=0):
    i = 0
    key = 0
    interval = 0 if fps == 0 else int(1000.0 / fps)
    frames = [f for f in movie]
    while key != 27:
        cv2.imshow('win',frames[i])
        key = cv2.waitKey(interval)
        if key == 2555904 or key < 0:
            i = i+1
        elif key == 2424832:
            i = i-1
        i = 0 if i < 0 else len(frames)-1 if i >= len(frames) else i
    cv2.destroyWindow('win')
    del frames
    
def savemovie(frames,filename,fps,fourcc=cv2.cv.CV_FOURCC('F','M','P','4')):
    writer = None
    for frame in frames:
        if writer is None:
            frameSize = frames[0].shape
            writer = cv2.VideoWriter(filename,fourcc,fps,frameSize)
            
        writer.write(frame)
    writer.release()
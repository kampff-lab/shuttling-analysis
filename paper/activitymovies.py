# -*- coding: utf-8 -*-
"""
Created on Sun Sep 28 11:31:29 2014

@author: Gonçalo
"""

import os
import cv2
import video
import bisect
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

#datafolder = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data'
datafolder = r'D:/Protocols/Shuttling/LightDarkServoStable/Data'

class framesiterable:
    def __init__(self, path, frames):
        self.path = path
        self.frames = frames
        
    def __iter__(self):
        capture = cv2.VideoCapture(self.path)
        try:
            prev = None
            for i in self.frames:
                if prev is None or (i - prev) != 1:
                    capture.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, i)
                ret, frame = capture.read()
                if not ret:
                    break
                prev = i
                yield frame
        finally:
            capture.release()
            
def getrelativepath(sessioninfo,path):
    info = sessioninfo.dirname.reset_index()
    result = info.apply(lambda x:os.path.join(datafolder,
                                              x.subject,
                                              x.dirname,
                                              path),axis=1)
    result.index = sessioninfo.index
    result.name = 'path'
    return result
    
def readframe(frame):
    index = movie.capture.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)
    result, frame = movie.capture.read()
    cv2.putText(frame,str(int(index)),(0,30),
                cv2.cv.CV_FONT_HERSHEY_COMPLEX,1,
                (255,255,255,255))
    return frame, index
    
def showmovies(movies,fps=0):
    done = False
    mvs = movies.reset_index()
    interval = 0 if fps == 0 else int(1000.0 / fps)
    for subject,session,index,movie in mvs.values:
        for frame in movie:
            cv2.putText(frame,
                str.format('{0} session {1} ({2})',subject,session,index),
                (0,30),
                cv2.cv.CV_FONT_HERSHEY_COMPLEX,1,
                (255,255,255,255))
            cv2.imshow('win',frame)
            key = cv2.waitKey(interval)
            if key == 2228224: #page down
                break
            elif key == 27:
                done = True
                break
        if done:
            break
    cv2.destroyWindow('win')
    
def showcrossingmovies(crossings,sessioninfo):
    moviepath = getmoviepath(sessioninfo)
#    cr = crossings.reset_index('index').join(moviepath)
    cr = crossings.join(moviepath)
    cr.set_index('index',append=True,inplace=True)
    mvs = cr.apply(lambda x:
        framesiterable(x.path,
                       xrange(x.slices.start,x.slices.stop)),
                       axis=1)
    showmovies(mvs,fps=120)
    
#def getmovieframe(activity,key,sessioninfo):
#    entry = sessioninfo.loc[key[0:2]]
#    subject = key[0]
#    moviepath = os.path.join(datafolder,subject,entry.dirname,'front_video.avi')
    
def getmovieframes(sessioninfo,frames):
    videos = []
    moviepath = getmoviepath(sessioninfo)
    cframes = frames.reset_index()
    clipshift = (cframes.subject != cframes.subject.shift()) |\
                (cframes.session != cframes.session.shift()) |\
                (cframes.frame.diff() > 1)
    cframes['_group_'] = clipshift.cumsum()
    for (subject,session,g),clip in cframes.groupby(['subject',
                                                     'session',
                                                     '_group_'],
                                                     sort=False):
        movie = moviepath.ix[(subject,session)]
        videos.append(framesiterable(movie,clip.frame))
    return (f for vid in videos for f in vid)

def getmoviepath(sessioninfo):
    return getrelativepath(sessioninfo,'front_video.avi')
    
def getwhiskermoviepath(sessioninfo):
    return getrelativepath(sessioninfo,'whisker_video.avi')

def gettimepath(sessioninfo):
    return getrelativepath(sessioninfo,'front_video.csv')
    
def getwhiskertimepath(sessioninfo):
    return getrelativepath(sessioninfo,'whisker_video.csv')
                                            
def getbackgroundpath(sessioninfo):
    return getrelativepath(sessioninfo,r'Analysis\Background')
    
def getmovies(sessioninfo):
    vidpaths = getmoviepath(sessioninfo)
    timepaths = gettimepath(sessioninfo)
    return pd.DataFrame([video.video(path,timepath)
                        for path,timepath in zip(vidpaths,timepaths)],
                        index=vidpaths.index)
    
def getbackground(path,time):
    if type(time) == np.datetime64:
        time = str(time)
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
            videos.append(framesiterable(path, xrange(startframe, stopframe)))
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
    
def savemovie(frames,filename,fps,fourcc=cv2.cv.CV_FOURCC('F','M','P','4'),
              isColor=True,flip=None):
    writer = None
    try:
        for frame in frames:
            if writer is None:
                frameSize = (frame.shape[1],frame.shape[0])
                writer = cv2.VideoWriter(filename,fourcc,fps,frameSize,isColor)
    
            if isColor and frame.ndim < 3:
                frame = cv2.cvtColor(frame,cv2.cv.CV_GRAY2BGR)
            if flip is not None:
                frame = cv2.flip(frame,flip)
            writer.write(frame)
    finally:
        if writer is not None:
            writer.release()
            

class MoviePlotter:
    def __init__(self,activity,info,key='frame'):
        self.fig = plt.figure()
        self.movies = getmovies(info)
        self.activity = activity
        self.nframes = len(activity)
        self.image = None
        self.key = key
        self.index = 0
        
        gs0 = gridspec.GridSpec(3,1)
        self.movax = plt.Subplot(self.fig, gs0[:-1])
        self.movax.set_axis_off()
        self.fig.add_subplot(self.movax)
        
        ncols = len(activity.columns.drop(key))
        gs01 = gridspec.GridSpecFromSubplotSpec(1,ncols, subplot_spec=gs0[-1])
        self.axes = [plt.Subplot(self.fig, gs01[:,i]) for i in range(ncols)]
        for ax,name in zip(self.axes,activity.columns.drop(key)):
            ax.set_title(name)
            self.fig.add_subplot(ax)
        plt.tight_layout()
        self.updateframe()
        self.fig.canvas.mpl_connect('key_press_event',self.onkeypress)
        self.fig.canvas.mpl_connect('key_release_event',self.onkeyrelease)
        self.fig.canvas.mpl_connect('close_event',self.onclose)
        self.keytimer = self.fig.canvas.new_timer()
        self.keytimer.add_callback(self.updatekey)
        self.activekey = None
        
    def release(self):
        for m in self.movies.values:
            m[0].release()
        plt.close(self.fig)
        
    def updateframe(self):
        frame = self.activity.ix[self.index,:]
        moviekey = frame.name[:2]
        movie = self.movies.loc[moviekey][0]
        frameindex = frame[self.key]
        movieframe = movie.frame(frameindex)
        if self.image is None:
            self.image = self.movax.imshow(movieframe,cmap='gray')
        else:
            self.image.set_data(movieframe)
        title = str.format("{0} frame: {1}",moviekey,frameindex)
        self.movax.set_title(title)
        
        offset = 100
        fmin = self.index-offset
        fmax = self.index+offset
        minindex = max(fmin,0)
        maxindex = min(fmax,self.nframes)
        data = self.activity.ix[minindex:maxindex,:].drop(self.key,axis=1)
        x = range(minindex-self.index,maxindex-self.index)
        for i,ax in enumerate(self.axes):
            if len(ax.lines) > 0:
                ax.lines.pop(0)
            ax.plot(x,data.ix[:,i],'b')
            ax.relim()
            ax.set_xlim(-offset,offset)
        self.fig.canvas.draw_idle()
        
    def updatekey(self):
        if self.activekey == 'left':
            self.index = max(self.index-1,0)
            self.updateframe()
        if self.activekey == 'right':
            self.index = min(self.index+1,self.nframes-1)
            self.updateframe()
        if self.activekey == 'pageup':
            self.index = max(self.index-10,0)
            self.updateframe()
        if self.activekey == 'pagedown':
            self.index = min(self.index+10,self.nframes-1)
            self.updateframe()
        if self.activekey == 'home':
            self.index = max(self.index-100,0)
            self.updateframe()
        if self.activekey == 'end':
            self.index = min(self.index+100,self.nframes-1)
            self.updateframe()
        
    def onclose(self, evt):
        self.release()
        
    def onkeypress(self, evt):
        self.activekey = evt.key
        self.updatekey()
        self.keytimer.start(interval=150)
            
    def onkeyrelease(self, evt):
        if self.activekey == evt.key:
            self.activekey = None
            self.keytimer.stop()

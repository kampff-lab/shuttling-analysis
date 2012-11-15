# -*- coding: utf-8 -*-
"""
Created on Tue Jun 26 18:19:10 2012

@author: IntelligentSystems
"""

import cv
import os
import glob
import numpy as np
from collections import deque

def play_video(path,name,posmsec=0,fps=0):
    capture = cv.CaptureFromFile(path)
    if fps <= 0:
        fps = cv.GetCaptureProperty(capture,cv.CV_CAP_PROP_FPS)
    interval = int(1000.0 / fps)
    cv.SetCaptureProperty(capture,cv.CV_CAP_PROP_POS_MSEC,posmsec)

    playing = [True]
    cv.NamedWindow(name)
    def on_mouse(event, x, y, flags, param):
        if event == cv.CV_EVENT_RBUTTONDOWN:
            playing[0] = False
    cv.SetMouseCallback(name, on_mouse)
    
    while playing[0]:
        frame = cv.QueryFrame(capture)
        if frame is None:
            playing[0] = False
        else:
            cv.ShowImage(name,frame)
            cv.WaitKey(interval)
        
    cv.DestroyWindow(name)
    del capture

def load_image_folder(path,iscolor=True):
    images = []
    for infile in glob.glob(os.path.join(path, '*.png')):
        images.append(cv.LoadImage(infile,iscolor))
    return images
    
def pixel_distance_matrix(images):
    buf = cv.CreateImage(cv.GetSize(images[0]),images[0].depth,images[0].channels)
    distances = np.zeros((len(images), len(images)))
    for i in xrange(len(images)):
        for j in xrange(i+1,len(images)):
            cv.Sub(images[i],images[j],buf)
            cv.Pow(buf,buf,2)
            distance = cv.Sum(buf)[0]
            distances[i,j] = distance
            distances[j,i] = distance
    del buf
    return distances
    
def distance_clusters(distances,threshold):
    adjacencies = distances < threshold
    clusters = []
    assigned = []
    for i in xrange(len(adjacencies)):
        if not i in assigned:
            cluster = []
            queue = deque([i])
            while len(queue) > 0:
                n = queue.popleft()
                if not n in assigned:
                    for j in np.nonzero(adjacencies[n,:])[0]:
                        queue.append(j)
                    cluster.append(n)
                    assigned.append(n)
            clusters.append(cluster)
    return clusters
    
def average_image_list(images):
    result = None
    if len(images) > 0:
        scale = 1. / len(images)
        mean = cv.CreateImage(cv.GetSize(images[0]),cv.IPL_DEPTH_32F,images[0].channels)
        result = cv.CreateImage(cv.GetSize(images[0]),images[0].depth,images[0].channels)
        for image in images:
            cv.Add(image,mean,mean)
        cv.ConvertScale(mean,mean,scale)
        cv.ConvertScale(mean,result)
        del mean
    return result
    
def max_image_list(images):
    result = None
    for image in images:
        if result is None:
            result = cv.CloneImage(image)
        else:
            cv.Max(image,result,result)
    return result
    
def avgstd_image_list(images):
    mean = None
    std = None
    if len(images) > 0:
        scale = 1. / len(images)
        mean = cv.CreateImage(cv.GetSize(images[0]),cv.IPL_DEPTH_32F,images[0].channels)
        std = cv.CreateImage(cv.GetSize(images[0]),cv.IPL_DEPTH_32F,images[0].channels)
        buf = cv.CreateImage(cv.GetSize(images[0]),cv.IPL_DEPTH_32F,images[0].channels)
        for image in images:
            cv.Add(image,mean,mean)
            cv.Mul(image,image,buf)
            cv.Add(buf,std,std)
        cv.ConvertScale(mean,mean,scale)
        cv.ConvertScale(std,std,scale)
        cv.Mul(mean,mean,buf)
        cv.Sub(std,buf,std)
        cv.Pow(std,std,0.5)
        
        meanresult = cv.CreateImage(cv.GetSize(images[0]),images[0].depth,images[0].channels)
        stdresult = cv.CreateImage(cv.GetSize(images[0]),images[0].depth,images[0].channels)
        cv.ConvertScale(mean,meanresult)
        cv.ConvertScale(std,stdresult)
        del buf
        del std
        del mean
    return (meanresult,stdresult)
        
def save_clusters(images,clusters):
    os.makedirs("Clusters")
    for i in xrange(len(clusters)):
        for j in clusters[i]:
            cv.SaveImage(r"Clusters\cluster%s_image%s.bmp" % (i,j), images[j])
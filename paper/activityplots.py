# -*- coding: utf-8 -*-
"""
Created on Sun Sep 14 11:42:00 2014

@author: Gonçalo
"""

import os
import pltutils
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import activitytables
from preprocess import labelpath
from collectionselector import CollectionSelector

def barplot(data,column,by=None,ax=None):
    if ax is None:
        ax = plt.gca()
        
    groups = data.groupby(by)
    for group in groups:
        print group.key

def fpshist(activity,ax=None):
    if ax is None:
        ax = plt.gca()
    (1.0 / activity.timedelta).hist(ax=ax,bins=100,normed=True)
    ax.set_xlabel('fps')
    ax.set_title('frame rate')
    
def trajectoryplot(activity,crossings,ax=None,style='k',alpha=1):
    if ax is None:
        ax = plt.gca()
    for s in crossings.slices:
        ax.plot(activity.xhead[s],activity.yhead[s],style,alpha=alpha)
    ax.set_title('trajectories')
    ax.set_xlabel('x (cm)')
    ax.set_ylabel('y (cm)')
    
def featuresummary(crossings,ax=None,onselect=None):
    if ax is None:
        ax = plt.gca()
    pts = ax.scatter(crossings.duration,crossings.yhead_max,
               s=10,marker='D',facecolors='b',edgecolors='none')
    selector = CollectionSelector(ax,pts,color_other='r',
                                  onselection=onselect)
    ax.set_title('trajectory features')
    ax.set_xlabel('duration (s)')
    ax.set_ylabel('max height (cm)')
    return selector
    
def slowdownsummary(crossings,ax=None,regress=True):
    if ax is None:
        ax = plt.gca()
    entryspeed = crossings.entryspeed
    exitspeed = crossings.exitspeed
    ax.plot(entryspeed,exitspeed,'.')
    if regress:
        pltutils.regressionline(entryspeed,exitspeed,ax,color='k')
    ax.set_title('slowdown')
    ax.set_xlabel('entry speed (cm / s)')
    ax.set_ylabel('exit speed (cm / s)')
    
def rewardrate(rewards,ax=None):
    if ax is None:
        ax = plt.gca()
    intervals = rewards.time.diff() / np.timedelta64(1,'m')
    ax.plot(1.0 / intervals)
    ax.set_title('reward rate')
    ax.set_xlabel('trials')
    ax.set_ylabel('r.p.m')
    
def clearhandles(handles):
    while len(handles) > 0:
        handle = handles.pop()
        if np.iterable(handle):
            for l in handle:
                l.remove()
                del l
        del handle
        
def clearcollection(handles):
    while len(handles) > 0:
        handle = handles.pop()
        handle.remove()
        del handle

def sessionsummary(path):
    labelh5path = labelpath(path)
    activity, crossings = activitytables.read_crossings(path)
    rewards = activitytables.read_rewards(path)
    
    selected = []
    def onselect(ind):
        selector.ind[:] = ind
        selector.updateselection()
        clearhandles(selected)
        if len(ind) <= 0:
            return
        
        for s in crossings.slices[ind]:
            h = axs[0,1].plot(activity.xhead[s],activity.yhead[s],'r')
            selected.append(h)
            
    markers = []
    def updateplots():
        onselect([])
        clearcollection(markers)
        valid = crossings.label == 'valid'
        
        axs[0,1].clear()
        trajectoryplot(activity,crossings[valid],axs[0,1],alpha=0.2)
        
        axs[1,2].clear()
        slowdownsummary(crossings[valid],axs[1,2])
        
        invalid = crossings.label == 'invalid'
        if invalid.any():
            rows = crossings[invalid]
            pts = axs[0,2].scatter(rows.duration,rows.yhead_max,
                           s=20,marker='x',facecolors='none',edgecolors='r')
            markers.append(pts)
        fig.canvas.draw_idle()
            
    def onkeypress(evt):
        label = None
        if evt.key == 'q':
            crossings.label.to_hdf(labelh5path, 'label')
        if evt.key == 'r':
            label = 'invalid'
        if evt.key == 'v':
            label = 'valid'
        if label != None:
            crossings.label[selector.ind] = label
            updateplots()
    
    fig, axs = plt.subplots(3,3)
    fpshist(activity,axs[0,0])
    selector = featuresummary(crossings,axs[0,2],onselect)
    updateplots()
    rewardrate(rewards,axs[1,0])
    fig.canvas.mpl_connect('key_press_event',onkeypress)
    
    plt.tight_layout()
    return activity,crossings,rewards,selector